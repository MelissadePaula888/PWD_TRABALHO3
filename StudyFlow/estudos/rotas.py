import os
from datetime import date, datetime, timedelta
from functools import wraps

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from estudos import app, db
from estudos.modelos import (
    Aula, Conquista, Favorito, Flashcard, HistoricoXP, Materia, Meta, Modulo,
    Notificacao, Progresso, SessaoEstudo, Usuario, UsuarioConquista
)


def login_required_simples(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.path))
        return funcao(*args, **kwargs)
    return protegida


def adicionar_xp(usuario, quantidade, motivo):
    usuario.xp += quantidade
    novo_nivel = usuario.xp // 100 + 1
    if novo_nivel > usuario.level:
        usuario.level = novo_nivel
        db.session.add(Notificacao(
            usuario_id=usuario.id,
            title='Novo nível!',
            message=f'Você chegou ao nível {novo_nivel}!'
        ))
    db.session.add(HistoricoXP(usuario_id=usuario.id, amount=quantidade, reason=motivo))


def atualizar_streak(usuario):
    hoje = date.today()
    if usuario.last_study_date == hoje:
        return False
    if usuario.last_study_date == hoje - timedelta(days=1):
        usuario.streak += 1
    else:
        usuario.streak = 1
    usuario.best_streak = max(usuario.best_streak or 0, usuario.streak)
    usuario.last_study_date = hoje
    return True


def verificar_conquistas(usuario):
    aulas = Progresso.query.filter_by(usuario_id=usuario.id, completed=True).count()
    sessoes = SessaoEstudo.query.filter_by(usuario_id=usuario.id).count()
    regras = {
        'Primeiro passo': aulas >= 1,
        'Estudioso': aulas >= 10,
        '7 dias seguidos': usuario.streak >= 7,
        'Em evolução': usuario.level >= 5,
        'Maratonista': sessoes >= 10,
        'Lenda': usuario.xp >= 5000,
    }

    for nome, liberada in regras.items():
        conquista = Conquista.query.filter_by(name=nome).first()
        ja_tem = UsuarioConquista.query.filter_by(
            usuario_id=usuario.id,
            conquista_id=conquista.id if conquista else 0
        ).first()
        if conquista and liberada and not ja_tem:
            db.session.add(UsuarioConquista(usuario_id=usuario.id, conquista_id=conquista.id))
            adicionar_xp(usuario, conquista.reward_xp, f'Conquista: {nome}')
            db.session.add(Notificacao(
                usuario_id=usuario.id,
                title='Conquista desbloqueada!',
                message=nome
            ))


def concluir_aula(usuario, aula):
    progresso = Progresso.query.filter_by(usuario_id=usuario.id, aula_id=aula.id).first()
    if progresso and progresso.completed:
        return False
    if not progresso:
        progresso = Progresso(usuario_id=usuario.id, aula_id=aula.id)
        db.session.add(progresso)
    progresso.completed = True
    progresso.completed_at = datetime.utcnow()
    adicionar_xp(usuario, aula.xp_reward, f'Aula concluída: {aula.title}')
    atualizar_streak(usuario)
    verificar_conquistas(usuario)
    db.session.commit()
    return True


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('password', '')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password_hash, senha):
            login_user(usuario)
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('password', '')
        confirmar = request.form.get('confirm_password', '')

        if len(username) < 3 or len(username) > 80:
            flash('O usuário deve ter entre 3 e 80 caracteres.', 'danger')
        elif Usuario.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso.', 'danger')
        elif Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
        elif len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
        elif senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
        else:
            usuario = Usuario(
                username=username,
                email=email,
                password_hash=generate_password_hash(senha)
            )
            db.session.add(usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required_simples
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required_simples
def dashboard():
    materias = Materia.query.all()
    for materia in materias:
        aulas = Aula.query.join(Modulo).filter(Modulo.materia_id == materia.id).all()
        ids = [aula.id for aula in aulas]
        feitas = Progresso.query.filter(
            Progresso.usuario_id == current_user.id,
            Progresso.completed.is_(True),
            Progresso.aula_id.in_(ids)
        ).count() if ids else 0
        materia.progress_percent = int(feitas / len(aulas) * 100) if aulas else 0
        materia.total_duration = sum(aula.duration or 0 for aula in aulas)
        materia.lesson_count = len(aulas)

    total_lessons_done = Progresso.query.filter_by(usuario_id=current_user.id, completed=True).count()
    inicio_semana = datetime.utcnow() - timedelta(days=7)
    weekly_minutes = db.session.query(
        func.coalesce(func.sum(SessaoEstudo.duration_minutes), 0)
    ).filter(
        SessaoEstudo.usuario_id == current_user.id,
        SessaoEstudo.start_time >= inicio_semana
    ).scalar() or 0

    last_lesson = Aula.query.join(Progresso).filter(
        Progresso.usuario_id == current_user.id,
        Progresso.completed.is_(False)
    ).order_by(Progresso.id.desc()).first()
    if not last_lesson:
        last_lesson = Aula.query.order_by(Aula.id).first()

    return render_template(
        'dashboard.html',
        subjects=materias,
        total_lessons_done=total_lessons_done,
        weekly_minutes=weekly_minutes,
        last_lesson=last_lesson
    )


@app.route('/subjects')
@login_required_simples
def subjects():
    return render_template('subjects.html', subjects=Materia.query.all())


@app.route('/subjects/<int:subject_id>')
@login_required_simples
def subject_detail(subject_id):
    materia = Materia.query.get_or_404(subject_id)
    feitas = Progresso.query.filter_by(usuario_id=current_user.id, completed=True).all()
    done = {progresso.aula_id for progresso in feitas}
    return render_template('subject.html', subject=materia, done=done)


@app.route('/lesson/<int:lesson_id>')
@login_required_simples
def lesson(lesson_id):
    aula = Aula.query.get_or_404(lesson_id)
    progresso = Progresso.query.filter_by(
        usuario_id=current_user.id,
        aula_id=aula.id,
        completed=True
    ).first()
    return render_template('lesson.html', lesson=aula, completed=bool(progresso), flashcards=Flashcard.query.filter_by(lesson_id=aula.id).order_by(Flashcard.order).all())


@app.route('/lessons/<int:lesson_id>/complete', methods=['POST', 'GET'])
@login_required_simples
def complete(lesson_id):
    aula = Aula.query.get_or_404(lesson_id)
    if concluir_aula(current_user, aula):
        flash(f'+{aula.xp_reward} XP! Aula concluída.', 'success')
    else:
        flash('Esta aula já foi concluída.', 'success')
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/achievements')
@login_required_simples
def achievements():
    desbloqueadas = {
        item.conquista_id for item in UsuarioConquista.query.filter_by(usuario_id=current_user.id).all()
    }
    return render_template(
        'achievements.html',
        achievements=Conquista.query.all(),
        unlocked=desbloqueadas
    )


@app.route('/ranking')
@login_required_simples
def ranking():
    usuarios = Usuario.query.order_by(Usuario.xp.desc(), Usuario.id.asc()).all()
    return render_template('ranking.html', users=usuarios)


@app.route('/goals', methods=['GET', 'POST'])
@login_required_simples
def goals():
    if request.method == 'POST':
        meta = Meta(
            usuario_id=current_user.id,
            title=request.form.get('title', '').strip(),
            description=request.form.get('description'),
            target=max(1, int(request.form.get('target', 1))),
            goal_type=request.form.get('goal_type', 'lessons'),
            reward_xp=100
        )
        db.session.add(meta)
        db.session.commit()
        return redirect(url_for('goals'))

    metas = Meta.query.filter_by(usuario_id=current_user.id).order_by(
        Meta.completed.asc(), Meta.id.desc()
    ).all()

    aulas_feitas = Progresso.query.filter_by(usuario_id=current_user.id, completed=True).count()
    minutos_estudo = sum(
        sessao.duration_minutes or 0
        for sessao in SessaoEstudo.query.filter_by(usuario_id=current_user.id).all()
    )

    for meta in metas:
        if meta.goal_type == 'lessons':
            meta.progress = aulas_feitas
        elif meta.goal_type == 'xp':
            meta.progress = current_user.xp
        elif meta.goal_type == 'hours':
            meta.progress = int(minutos_estudo / 60)
        meta.progress = min(meta.progress, meta.target)
        if meta.progress >= meta.target and not meta.completed:
            meta.completed = True
            adicionar_xp(current_user, meta.reward_xp, f'Meta: {meta.title}')

    db.session.commit()
    return render_template('goals.html', goals=metas)


@app.route('/statistics')
@login_required_simples
def statistics():
    return render_template('statistics.html')


@app.route('/calendar')
@login_required_simples
def calendar():
    sessoes = SessaoEstudo.query.filter_by(usuario_id=current_user.id).all()
    days = {sessao.start_time.date().isoformat() for sessao in sessoes}
    return render_template('calendar.html', days=days, today=date.today())


@app.route('/study-timer', methods=['GET', 'POST'])
@login_required_simples
def timer():
    if request.method == 'POST':
        minutos = max(1, int(request.form.get('minutes', 25)))
        materia_id = request.form.get('subject_id') or None
        agora = datetime.utcnow()
        db.session.add(SessaoEstudo(
            usuario_id=current_user.id,
            materia_id=materia_id,
            start_time=agora - timedelta(minutes=minutos),
            end_time=agora,
            duration_minutes=minutos
        ))
        adicionar_xp(current_user, 10, 'Sessão de estudo')
        atualizar_streak(current_user)
        verificar_conquistas(current_user)
        db.session.commit()
        flash(f'Sessão de {minutos} minutos registrada! +10 XP', 'success')
        return redirect(url_for('timer'))
    return render_template('timer.html', subjects=Materia.query.all())


@app.route('/api/statistics')
@login_required_simples
def api_statistics():
    hoje = date.today()
    labels, minutes, xp = [], [], []

    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        labels.append(dia.strftime('%d/%m'))
        minutes.append(db.session.query(
            func.coalesce(func.sum(SessaoEstudo.duration_minutes), 0)
        ).filter(
            SessaoEstudo.usuario_id == current_user.id,
            func.date(SessaoEstudo.start_time) == dia
        ).scalar() or 0)
        xp.append(db.session.query(
            func.coalesce(func.sum(HistoricoXP.amount), 0)
        ).filter(
            HistoricoXP.usuario_id == current_user.id,
            func.date(HistoricoXP.created_at) == dia
        ).scalar() or 0)

    subject_labels, subject_values = [], []
    for materia in Materia.query.all():
        minutos = db.session.query(
            func.coalesce(func.sum(SessaoEstudo.duration_minutes), 0)
        ).filter(
            SessaoEstudo.usuario_id == current_user.id,
            SessaoEstudo.materia_id == materia.id
        ).scalar() or 0
        if minutos:
            subject_labels.append(materia.name)
            subject_values.append(minutos)

    return jsonify(
        labels=labels,
        minutes=minutes,
        xp=xp,
        subject_labels=subject_labels,
        subject_values=subject_values
    )


@app.route('/profile')
@login_required_simples
def profile():
    done_count = Progresso.query.filter_by(usuario_id=current_user.id, completed=True).count()
    sessoes = SessaoEstudo.query.filter_by(usuario_id=current_user.id).all()
    hours = round(sum(sessao.duration_minutes or 0 for sessao in sessoes) / 60, 1)
    achievements_list = UsuarioConquista.query.filter_by(usuario_id=current_user.id).all()
    return render_template(
        'profile.html',
        done_count=done_count,
        hours=hours,
        achievements=achievements_list
    )


@app.route('/profile/upload', methods=['POST'])
@login_required_simples
def profile_upload():
    arquivo = request.files.get('avatar')
    if not arquivo or not arquivo.filename:
        flash('Escolha uma imagem.', 'danger')
        return redirect(url_for('profile'))

    extensao = arquivo.filename.rsplit('.', 1)[-1].lower() if '.' in arquivo.filename else ''
    if extensao not in app.config['ALLOWED_EXTENSIONS']:
        flash('Formato não permitido. Use PNG, JPG, JPEG, WEBP ou GIF.', 'danger')
        return redirect(url_for('profile'))

    nome = secure_filename(f'user_{current_user.id}.{extensao}')
    arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome))
    current_user.avatar = nome
    db.session.commit()
    flash('Foto atualizada!', 'success')
    return redirect(url_for('profile'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required_simples
def settings():
    if request.method == 'POST':
        tema = request.form.get('theme', 'light')

        if tema not in ('light', 'dark'):
            tema = 'light'

        current_user.theme = tema
        db.session.commit()
        flash('Configurações salvas!', 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html')
