// StudyFlow — interações gerais

document.addEventListener('DOMContentLoaded', () => {
    // Remove avisos depois de alguns segundos.
    setTimeout(() => {
        document.querySelectorAll('.flash').forEach(elemento => {
            elemento.classList.add('flash-hide');
            setTimeout(() => elemento.remove(), 250);
        });
    }, 4500);

    // Entrada suave dos principais elementos da página.
    document.querySelectorAll('.panel, .stat-card, .subject, .module-card, .achievement, .settings-card').forEach((elemento, index) => {
        elemento.classList.add('js-reveal');
        elemento.style.setProperty('--delay', `${Math.min(index * 45, 260)}ms`);
    });

    requestAnimationFrame(() => {
        document.querySelectorAll('.js-reveal').forEach(elemento => {
            elemento.classList.add('show');
        });
    });

    // Pequeno efeito de clique nos botões.
    document.querySelectorAll('.btn').forEach(botao => {
        botao.addEventListener('click', () => {
            botao.classList.add('is-clicked');
            setTimeout(() => botao.classList.remove('is-clicked'), 180);
        });
    });

    // Destaque automático do item atual do menu.
    const paginaAtual = window.location.pathname;
    document.querySelectorAll('.sidebar nav a, .side-bottom a').forEach(link => {
        try {
            const url = new URL(link.href, window.location.origin);
            if (url.pathname !== '/' && paginaAtual.startsWith(url.pathname)) {
                link.classList.add('active');
            }
        } catch (erro) {
            // Ignora links inválidos sem quebrar o restante da página.
        }
    });
});

// Pomodoro
let seconds = 1500;
let interval = null;

function setMinutes(m) {
    seconds = m * 60;
    const input = document.getElementById('minutesInput');
    if (input) input.value = m;
    draw();
}

function draw() {
    const timer = document.getElementById('timer');
    if (!timer) return;

    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    timer.textContent = `${m}:${s}`;
}

function startTimer() {
    if (interval) return;

    interval = setInterval(() => {
        if (seconds > 0) {
            seconds--;
            draw();
        } else {
            clearInterval(interval);
            interval = null;
            alert('Foco concluído! Registre a sessão para ganhar XP.');
        }
    }, 1000);
}

function resetTimer() {
    clearInterval(interval);
    interval = null;
    setMinutes(25);
}

draw();

// Flashcards
const dadosFlashcards = document.getElementById('flashcards-data');

if (dadosFlashcards) {
    const cartao = document.getElementById('flashcard');
    let indiceFlashcard = 0;

    function atualizarFlashcard() {
        document.getElementById('flashcard-question').textContent = flashcards[indiceFlashcard];
        document.getElementById('flashcard-answer').textContent = respostas[indiceFlashcard];
        document.getElementById('flashcard-count').textContent =
            `${indiceFlashcard + 1} / ${flashcards.length}`;

        cartao.classList.remove('virado');
    }

    function virarFlashcard() {
        cartao.classList.toggle('virado');
    }

    function proximoFlashcard() {
        indiceFlashcard = (indiceFlashcard + 1) % flashcards.length;
        atualizarFlashcard();
    }

    function anteriorFlashcard() {
        indiceFlashcard = (indiceFlashcard - 1 + flashcards.length) % flashcards.length;
        atualizarFlashcard();
    }

    atualizarFlashcard();
}


// Tema: aplica a preferência imediatamente e mantém o visual consistente.
(function () {
    const body = document.body;
    const temaSalvo = localStorage.getItem('studyflow-theme');

    function aplicarTema(theme) {
        const tema = theme === 'dark' ? 'dark' : 'light';
        body.classList.remove('theme-light', 'theme-dark');
        body.classList.add(`theme-${tema}`);
        body.dataset.theme = tema;
    }

    // A preferência salva localmente só é usada para deixar a troca instantânea.
    if (temaSalvo) {
        aplicarTema(temaSalvo);
    }

    window.aplicarTemaStudyFlow = aplicarTema;

    document.querySelectorAll('[data-theme-option]').forEach(opcao => {
        opcao.addEventListener('click', () => {
            const radio = opcao.querySelector('input[type="radio"]');
            if (!radio) return;
            radio.checked = true;
            aplicarTema(radio.value);
            localStorage.setItem('studyflow-theme', radio.value);
        });
    });
})();
