from datetime import datetime
from flask_login import UserMixin
from estudos import db


class Usuario(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255))
    theme = db.Column(db.String(10), default='light')
    language = db.Column(db.String(5), default='pt')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def level_xp(self):
        return (self.level - 1) * 100

    @property
    def next_level_xp(self):
        return self.level * 100

    @property
    def level_progress(self):
        total = self.next_level_xp - self.level_xp
        return int(max(0, min(100, ((self.xp - self.level_xp) / total) * 100))) if total else 100


class Materia(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='book')
    color = db.Column(db.String(7), default='#6c5ce7')
    modulos = db.relationship('Modulo', backref='materia', cascade='all, delete-orphan', order_by='Modulo.order')

    @property
    def modules(self):
        return self.modulos


class Modulo(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    xp_reward = db.Column(db.Integer, default=150)
    aulas = db.relationship('Aula', backref='modulo', cascade='all, delete-orphan', order_by='Aula.order')

    @property
    def lessons(self):
        return self.aulas

    @property
    def subject(self):
        return self.materia


class Aula(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column('module_id', db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(300))
    duration = db.Column(db.Integer, default=15)
    order = db.Column(db.Integer, default=0)
    xp_reward = db.Column(db.Integer, default=50)
    flashcards = db.relationship('Flashcard', backref='aula', cascade='all, delete-orphan', order_by='Flashcard.order')

    @property
    def module(self):
        return self.modulo

    @property
    def video_embed_url(self):
        if not self.video_url:
            return None
        url = self.video_url.strip()
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/', 1)[1].split('?', 1)[0].split('&', 1)[0]
            return f'https://www.youtube.com/embed/{video_id}'
        if 'youtube.com/watch' in url and 'v=' in url:
            video_id = url.split('v=', 1)[1].split('&', 1)[0]
            return f'https://www.youtube.com/embed/{video_id}'
        if 'youtube.com/embed/' in url:
            return url.split('?', 1)[0]
        return url


class Flashcard(db.Model):
    __tablename__ = 'flashcard'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)


class Progresso(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    aula_id = db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='uq_usuario_aula'),)


class SessaoEstudo(db.Model):
    __tablename__ = 'study_session'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    materia_id = db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'))
    aula_id = db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=0)


class HistoricoXP(db.Model):
    __tablename__ = 'xp_history'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Conquista(db.Model):
    __tablename__ = 'achievement'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default='trophy')
    requirement = db.Column(db.Integer, default=1)
    reward_xp = db.Column(db.Integer, default=100)


class UsuarioConquista(db.Model):
    __tablename__ = 'user_achievement'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    conquista_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'conquista_id', name='uq_usuario_conquista'),)


class Meta(db.Model):
    __tablename__ = 'goal'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    target = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Integer, default=0)
    goal_type = db.Column(db.String(30), default='lessons')
    deadline = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    reward_xp = db.Column(db.Integer, default=100)


class Favorito(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    aula_id = db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='uq_favorito'),)


class Notificacao(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
