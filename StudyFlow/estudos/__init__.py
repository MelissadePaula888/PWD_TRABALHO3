from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'studyflow-dev-secret-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studyflow_novo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = str(BASE_DIR / 'static' / 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from estudos import modelos


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(modelos.Usuario, int(usuario_id))


# Conteúdo das videoaulas e flashcards.
# Cada item é: título, link do vídeo e lista de (pergunta, resposta).
CONTEUDO = {
    'Matemática': [
        ('Adição e Subtração', 'https://youtu.be/e78_5WIssSU?si=_vGkBs3B5Aqa51_2', [
            ('Quanto é 27 + 35?', '62.'),
            ('Quanto é 84 - 29?', '55.'),
            ('Calcule: 125 + 48 - 30.', '143.'),
            ('Uma pessoa tinha R$ 100 e gastou R$ 37. Quanto sobrou?', 'R$ 63.'),
            ('Calcule: 250 - 75 + 18.', '193.')
        ]),
        ('Fração', 'https://youtu.be/RbLQCSB4EUY?si=8A2SQCOCbBYdmULO', [
            ('Em 3/7, qual é o numerador?', '3.'),
            ('Em 5/9, qual é o denominador?', '9.'),
            ('Calcule: 2/5 + 1/5.', '3/5.'),
            ('Calcule: 7/8 - 3/8.', '4/8 = 1/2.'),
            ('Calcule: 1/2 + 1/4.', '3/4.')
        ]),
        ('Regra de 3', 'https://youtu.be/alLifth7gxE?si=xeHmyDs79skSw3nH', [
            ('Se 2 cadernos custam R$ 18, quanto custam 5?', 'R$ 45.'),
            ('3 trabalhadores fazem um serviço em 12 dias. 6 trabalhadores levam quantos dias?', '6 dias.'),
            ('Se 4 kg de arroz custam R$ 28, quanto custam 7 kg?', 'R$ 49.'),
            ('Se 5 máquinas produzem 100 peças, quantas 8 máquinas produzem na mesma proporção?', '160 peças.'),
            ('Se 6 canetas custam R$ 12, quanto custam 15 canetas?', 'R$ 30.')
        ]),
        ('Função: Noção Básica', 'https://youtu.be/SPZqQ5qn3P0?si=8jQFASSF_p_oY19w', [
            ('O que é uma função?', 'Uma relação em que cada entrada possui uma única saída.'),
            ('O que é domínio?', 'O conjunto dos valores de entrada permitidos.'),
            ('O que é imagem?', 'O conjunto dos valores de saída obtidos.'),
            ('Se f(x) = x + 2, quanto vale f(5)?', '7.'),
            ('Se f(x) = 2x + 1, quanto vale f(3)?', '7.')
        ]),
        ('Iniciação à Função Afim', 'https://youtu.be/hdMFlAv5GkU?si=zMG84X0VNiCUl_Y6', [
            ('Qual é a forma geral da função afim?', 'f(x) = ax + b.'),
            ('Na função f(x) = 3x + 2, quanto vale f(4)?', '14.'),
            ('Na função f(x) = 5x - 1, qual é o coeficiente angular?', '5.'),
            ('Na função f(x) = 2x + 7, qual é o valor de f(0)?', '7.'),
            ('Na função f(x) = 4x - 8, qual é a raiz?', 'x = 2.')
        ]),
    ],
    'Física': [
        ('Conceitos Iniciais', 'https://youtu.be/2yHLrXMu-tE?si=gvfg-MVN88PrSIk0', [
            ('O que é uma grandeza física?', 'Uma propriedade que pode ser medida.'),
            ('Qual é a unidade de comprimento no SI?', 'Metro (m).'),
            ('O que é deslocamento?', 'A variação da posição de um corpo.'),
            ('O que é movimento?', 'A mudança da posição em relação a um referencial.'),
            ('O que é referencial?', 'O ponto ou sistema usado para analisar a posição e o movimento.')
        ]),
        ('Velocidade Média', 'https://youtu.be/2yHLrXMu-tE?si=4A-6fC3BEET-tb7c', [
            ('Qual é a fórmula da velocidade média?', 'Vm = ΔS / Δt.'),
            ('Um carro percorre 120 km em 2 h. Qual é a velocidade média?', '60 km/h.'),
            ('Um ciclista percorre 30 m em 5 s. Qual é a velocidade média?', '6 m/s.'),
            ('O que representa Δt?', 'A variação do tempo.'),
            ('Um carro percorre 200 km em 4 h. Qual é a velocidade média?', '50 km/h.')
        ]),
        ('Mecânica para ENEM', 'https://www.youtube.com/live/AvKBpHAVVtg?si=1zaKWUlvNs2zAbzw', [
            ('O que estuda a mecânica?', 'Movimento, equilíbrio e forças.'),
            ('O que é força?', 'Uma interação capaz de alterar o movimento ou deformar um corpo.'),
            ('Qual lei relaciona força, massa e aceleração?', 'A segunda Lei de Newton: F = m · a.'),
            ('Uma força de 20 N atua em uma massa de 5 kg. Qual é a aceleração?', '4 m/s².'),
            ('Qual é a unidade de força no SI?', 'Newton (N).')
        ]),
    ],
    'Química': [
        ('Fundamentos da Química Geral', 'https://youtu.be/XDBwYrWFZUQ?si=NTWNoXW5bXhGgnpF', [
            ('O que é matéria?', 'Tudo que possui massa e ocupa lugar no espaço.'),
            ('Quais são três estados físicos comuns da matéria?', 'Sólido, líquido e gasoso.'),
            ('O que é uma substância?', 'Matéria com composição e propriedades definidas.'),
            ('O que é uma mistura?', 'A união de duas ou mais substâncias.'),
            ('Qual é a diferença básica entre substância e mistura?', 'A substância possui composição definida; a mistura reúne duas ou mais substâncias.')
        ]),
        ('Função Inorgânica', 'https://youtu.be/U7no8O1hrLE?si=Wp7vgPNTOq_tb16e', [
            ('Quais são as principais funções inorgânicas?', 'Ácidos, bases, sais e óxidos.'),
            ('O que caracteriza uma base em água?', 'Geralmente libera íons OH⁻.'),
            ('O que caracteriza um ácido em água?', 'Geralmente libera íons H⁺.'),
            ('O que é um óxido?', 'Composto formado por oxigênio ligado a outro elemento.'),
            ('Qual função inorgânica é associada ao HCl?', 'Ácido.')
        ]),
        ('Estequiometria e Termoquímica', 'https://youtu.be/lj8yIGefzvI?si=PDv3APJZv7jgxvWp', [
            ('O que estuda a estequiometria?', 'As relações quantitativas entre reagentes e produtos.'),
            ('Por que uma equação química deve ser balanceada?', 'Para respeitar a conservação dos átomos.'),
            ('O que é uma reação exotérmica?', 'Uma reação que libera energia para o ambiente.'),
            ('O que estuda a termoquímica?', 'As variações de energia, especialmente calor, nas transformações químicas.'),
            ('O que é uma reação endotérmica?', 'Uma reação que absorve energia do ambiente.')
        ]),
    ],
    'Português': [
        ('Classes Gramaticais', 'https://youtu.be/2tMS1O3xn24?si=M6uZ4hcBRwtvrPDe', [
            ('O que é um substantivo?', 'Palavra que nomeia seres, objetos, lugares, sentimentos etc.'),
            ('O que é um adjetivo?', 'Palavra que caracteriza um substantivo.'),
            ('O que é um verbo?', 'Palavra que pode indicar ação, estado ou fenômeno.'),
            ('O que é um pronome?', 'Palavra que pode substituir ou acompanhar um substantivo.'),
            ('Na frase “A menina estudou”, qual é o verbo?', 'Estudou.')
        ]),
        ('Concordância', 'https://youtu.be/1IRO-p95oo0?si=g50Hgb6HuLiebVFK', [
            ('O que é concordância verbal?', 'A relação entre o verbo e o sujeito.'),
            ('O que é concordância nominal?', 'A relação de concordância entre os termos nominais.'),
            ('Na frase “Os alunos estudam”, por que “estudam” está no plural?', 'Porque concorda com o sujeito “os alunos”.'),
            ('Complete: “As meninas ___ cedo.”', 'chegaram.'),
            ('Complete: “Os livros ___ sobre a mesa.”', 'estão.')
        ]),
        ('Interpretação de Texto', 'https://youtu.be/XsN0e_xPyNI?si=f2gjemJ4lOCulyd-', [
            ('O que é ideia principal?', 'A informação central desenvolvida pelo texto.'),
            ('O que é inferência?', 'Uma conclusão obtida a partir das informações do texto.'),
            ('O que deve ser observado na interpretação?', 'Contexto, informações explícitas, implícitas e intenção.'),
            ('O que é uma informação implícita?', 'Uma informação que não está escrita diretamente, mas pode ser compreendida pelo contexto.'),
            ('O que é informação explícita?', 'Uma informação apresentada diretamente no texto.')
        ]),
    ],
    'História': [
        ('Brasil Imperial', 'https://youtu.be/eERlMeLvQlI?si=9savCV9rtayerWjh', [
            ('Quando começou o Brasil Império?', 'Em 1822, após a Independência.'),
            ('Quem governou durante o Segundo Reinado?', 'D. Pedro II.'),
            ('Qual lei aboliu oficialmente a escravidão?', 'Lei Áurea, em 1888.'),
            ('O que aconteceu em 1889?', 'A Proclamação da República.'),
            ('Quem foi o primeiro imperador do Brasil?', 'D. Pedro I.')
        ]),
        ('Revolução Industrial', 'https://youtu.be/t6nJNv-pNr8?si=Mpv59u0dQBoA-gac', [
            ('Onde começou a Revolução Industrial?', 'Na Inglaterra.'),
            ('Qual setor teve grande destaque no início?', 'O setor têxtil.'),
            ('O que mudou na produção?', 'A produção passou progressivamente do artesanato para fábricas mecanizadas.'),
            ('Qual fonte de energia teve grande importância na primeira Revolução Industrial?', 'O carvão mineral.'),
            ('Qual foi uma consequência social da industrialização?', 'O crescimento das cidades e do trabalho fabril.')
        ]),
        ('Guerra Fria', 'https://youtu.be/eQ08AS5ZHQQ?si=-oOFbKMLEUXlQae6', [
            ('O que foi a Guerra Fria?', 'Uma disputa política, econômica, militar e ideológica entre EUA e URSS.'),
            ('Quais superpotências lideravam os blocos?', 'Estados Unidos e União Soviética.'),
            ('Quais ideologias estavam em disputa?', 'Capitalismo e socialismo.'),
            ('O que foi a corrida espacial?', 'A disputa tecnológica entre EUA e URSS pela liderança espacial.'),
            ('Qual muro se tornou um dos símbolos da Guerra Fria?', 'O Muro de Berlim.')
        ]),
        ('1ª Guerra Mundial', 'https://youtu.be/EEOYAN2CWwM?si=HppRnEK-atl2rvU-', [
            ('Em que período ocorreu a Primeira Guerra Mundial?', '1914–1918.'),
            ('Qual acontecimento é tradicionalmente apontado como estopim?', 'O assassinato do arquiduque Francisco Ferdinando.'),
            ('Quais eram os principais blocos?', 'Tríplice Entente e Tríplice Aliança.'),
            ('Em que ano terminou a guerra?', '1918.'),
            ('Qual tratado ficou associado ao fim da guerra para a Alemanha?', 'Tratado de Versalhes.')
        ]),
        ('2ª Guerra Mundial', 'https://youtu.be/75eeykQFbdU?si=Pr6bMCL6Yd4ZTpxm', [
            ('Em que período ocorreu a Segunda Guerra Mundial?', '1939–1945.'),
            ('Quais eram os principais grupos?', 'Eixo e Aliados.'),
            ('Qual acontecimento levou os EUA a entrarem diretamente na guerra?', 'O ataque a Pearl Harbor.'),
            ('Em que ano terminou a Segunda Guerra Mundial?', '1945.'),
            ('Qual país foi invadido pela Alemanha em 1939, dando início à guerra na Europa?', 'Polônia.')
        ]),
    ],
    'Biologia': [
        ('Citologia', 'https://youtu.be/N33jWXzV8RU?si=X5RcWpiVy1fVmiK-', [
            ('O que é uma célula?', 'A unidade estrutural e funcional básica dos seres vivos.'),
            ('Qual é a função do núcleo?', 'Abrigar o material genético e participar do controle celular.'),
            ('Qual é a função da mitocôndria?', 'Participar da produção de energia para a célula.'),
            ('Qual é a função da membrana plasmática?', 'Controlar a entrada e saída de substâncias.'),
            ('Qual organela está relacionada à síntese de proteínas?', 'Ribossomo.')
        ]),
        ('Genética', 'https://youtu.be/tUtj4HIg4Wo?si=Xr15bZBfQQdtg6Uh', [
            ('O que é genética?', 'Área da Biologia que estuda a hereditariedade e a variação.'),
            ('O que é um gene?', 'Uma unidade de informação genética localizada no DNA.'),
            ('Quem é considerado o pai da genética?', 'Gregor Mendel.'),
            ('O que é genótipo?', 'O conjunto de informações genéticas de um indivíduo.'),
            ('O que é fenótipo?', 'Características observáveis resultantes da interação entre genética e ambiente.')
        ]),
        ('Ecologia', 'https://youtu.be/KKELP-3_Dlk?si=1SPgzRu2E9gwitIi', [
            ('O que estuda a ecologia?', 'As relações dos seres vivos entre si e com o ambiente.'),
            ('O que é uma cadeia alimentar?', 'Sequência em que ocorre transferência de matéria e energia pela alimentação.'),
            ('O que são produtores?', 'Organismos capazes de produzir seu próprio alimento, geralmente por fotossíntese.'),
            ('O que é um ecossistema?', 'Conjunto formado pelos seres vivos e pelos fatores não vivos de um ambiente.'),
            ('O que são consumidores?', 'Organismos que obtêm matéria e energia alimentando-se de outros organismos.')
        ]),
    ],
}

MODULOS = {
    'Matemática': [
        ('Aritmética', ['Adição e Subtração', 'Fração', 'Regra de 3']),
        ('Funções', ['Função: Noção Básica', 'Iniciação à Função Afim']),
        ('Álgebra', [])
    ],
    'Português': [
        ('Classes Gramaticais', ['Classes Gramaticais']),
        ('Concordância', ['Concordância']),
        ('Interpretação de Texto', ['Interpretação de Texto'])
    ],
    'História': [
        ('Brasil Imperial', ['Brasil Imperial']),
        ('Revolução Industrial', ['Revolução Industrial']),
        ('Guerras Mundiais e Guerra Fria', ['Guerra Fria', '1ª Guerra Mundial', '2ª Guerra Mundial'])
    ],
    'Física': [
        ('Conceitos Iniciais', ['Conceitos Iniciais']),
        ('Velocidade Média', ['Velocidade Média']),
        ('Mecânica', ['Mecânica para ENEM'])
    ],
    'Biologia': [
        ('Citologia', ['Citologia']),
        ('Genética', ['Genética']),
        ('Ecologia', ['Ecologia'])
    ],
    'Química': [
        ('Fundamentos da Química Geral', ['Fundamentos da Química Geral']),
        ('Função Inorgânica', ['Função Inorgânica']),
        ('Estequiometria e Termoquímica', ['Estequiometria e Termoquímica'])
    ],
}


def garantir_conteudo():
    from werkzeug.security import generate_password_hash

    if not modelos.Usuario.query.filter_by(email='admin@studyflow.local').first():
        db.session.add(modelos.Usuario(
            username='admin',
            email='admin@studyflow.local',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        ))

    if not modelos.Usuario.query.filter_by(email='demo@studyflow.local').first():
        db.session.add(modelos.Usuario(
            username='demo',
            email='demo@studyflow.local',
            password_hash=generate_password_hash('123456')
        ))

    db.session.flush()

    cores = {
        'Matemática': '#7c3aed', 'Português': '#ec4899', 'História': '#f59e0b',
        'Física': '#06b6d4', 'Biologia': '#10b981', 'Química': '#8b5cf6'
    }
    icones = {
        'Matemática': 'calculator', 'Português': 'book', 'História': 'landmark',
        'Física': 'atom', 'Biologia': 'leaf', 'Química': 'flask'
    }

    for nome, conteudos in CONTEUDO.items():
        materia = modelos.Materia.query.filter_by(name=nome).first()
        if not materia:
            materia = modelos.Materia(
                name=nome,
                description=f'Conteúdos de {nome}.',
                icon=icones[nome],
                color=cores[nome]
            )
            db.session.add(materia)
            db.session.flush()

        for numero, (nome_modulo, _) in enumerate(MODULOS[nome], 1):
            modulo = modelos.Modulo.query.filter_by(
                materia_id=materia.id,
                order=numero
            ).first()
            if not modulo:
                modulo = modelos.Modulo(
                    materia_id=materia.id,
                    name=nome_modulo,
                    description=f'Conteúdos de {nome_modulo}.',
                    order=numero
                )
                db.session.add(modulo)
                db.session.flush()
            else:
                modulo.name = nome_modulo
                modulo.description = f'Conteúdos de {nome_modulo}.'

        aulas = sorted(
            [a for m in materia.modulos for a in m.aulas],
            key=lambda a: (a.modulo.order, a.order)
        )

        # Garante exatamente a quantidade necessária para os conteúdos enviados.
        for indice in range(len(aulas), len(conteudos)):
            modulo = materia.modulos[min(indice // 3, len(materia.modulos) - 1)]
            aula = modelos.Aula(
                modulo_id=modulo.id,
                title=f'Aula {indice + 1}: {nome}',
                content='',
                duration=20,
                order=len(modulo.aulas) + 1
            )
            db.session.add(aula)
            db.session.flush()
            aulas.append(aula)

        for indice, (titulo, video, cards) in enumerate(conteudos):
            aula = aulas[indice]
            aula.title = titulo
            aula.video_url = video
            aula.duration = 20
            aula.content = (
                f'<h2>{titulo}</h2>'
                '<p>Assista à videoaula, revise o conteúdo e depois teste seus conhecimentos nos flashcards.</p>'
            )

            existentes = {card.order: card for card in aula.flashcards}
            for ordem, (pergunta, resposta) in enumerate(cards, 1):
                card = existentes.get(ordem)
                if card:
                    card.question = pergunta
                    card.answer = resposta
                else:
                    db.session.add(modelos.Flashcard(
                        lesson_id=aula.id,
                        question=pergunta,
                        answer=resposta,
                        order=ordem
                    ))

        # Organiza cada aula no módulo que realmente corresponde ao assunto.
        for numero, (_, titulos) in enumerate(MODULOS[nome], 1):
            modulo = modelos.Modulo.query.filter_by(
                materia_id=materia.id,
                order=numero
            ).first()
            for aula in modelos.Aula.query.filter_by(modulo_id=modulo.id).all():
                if aula.title not in titulos:
                    continue
            for titulo in titulos:
                aula = modelos.Aula.query.filter_by(
                    title=titulo
                ).join(modelos.Modulo).filter(
                    modelos.Modulo.materia_id == materia.id
                ).first()
                if aula:
                    aula.modulo_id = modulo.id

    if modelos.Conquista.query.count() == 0:
        conquistas = [
            ('Primeiro passo', 'Conclua sua primeira aula', 'flag', 1, 50),
            ('Estudioso', 'Conclua 10 aulas', 'book', 10, 100),
            ('7 dias seguidos', 'Mantenha um streak de 7 dias', 'fire', 7, 200),
            ('Em evolução', 'Chegue ao nível 5', 'bolt', 5, 250),
            ('Maratonista', 'Faça 10 sessões de estudo', 'clock', 10, 250),
            ('Lenda', 'Alcance 5000 XP', 'crown', 5000, 500),
        ]
        for nome, descricao, icone, requisito, xp in conquistas:
            db.session.add(modelos.Conquista(
                name=nome,
                description=descricao,
                icon=icone,
                requirement=requisito,
                reward_xp=xp
            ))

    db.session.commit()


with app.app_context():
    db.create_all()
    garantir_conteudo()

from estudos import rotas
