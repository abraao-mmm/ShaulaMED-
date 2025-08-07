// app.js

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const firebaseConfig = {
    apiKey: "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE", // Garanta que esta configuração está 100% correta
    authDomain: "shaulamed-mvp.firebaseapp.com",
    projectId: "shaulamed-mvp",
    storageBucket: "shaulamed-mvp.firebasestorage.app",
    messagingSenderId: "1089322609573",
    appId: "1:1089322609573:web:8cd64115a76c03fbb5d64c"
};

// --- INICIALIZAÇÃO DO FIREBASE ---
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// --- GERENCIAMENTO DE ESTADO ---
let currentUser = null;

// --- ELEMENTOS DA UI ---
const loadingContainer = document.getElementById('loading-container');
const loginContainer = document.getElementById('login-container');
const signupContainer = document.getElementById('signup-container');
const mainContainer = document.querySelector('.main-container');

// --- FUNÇÕES DE UI ---
function showScreen(screen) {
    // Esconde todos os containers primeiro
    if (loadingContainer) loadingContainer.style.display = 'none';
    if (loginContainer) loginContainer.style.display = 'none';
    if (signupContainer) signupContainer.style.display = 'none';
    if (mainContainer) mainContainer.style.display = 'none';

    // Mostra o container desejado
    if (screen === 'login' && loginContainer) loginContainer.style.display = 'grid';
    if (screen === 'signup' && signupContainer) signupContainer.style.display = 'grid';
    if (screen === 'app' && mainContainer) mainContainer.style.display = 'block';
    if (screen === 'loading' && loadingContainer) loadingContainer.style.display = 'flex';
}

function notify(message, isError = false) {
    // Implementação simples de notificação
    alert(message); 
}

// --- LÓGICA DE LOGIN ---
async function handleLogin(event) {
    event.preventDefault();
    console.log("Tentativa de login iniciada...");
    const email = document.getElementById('login-email-input').value;
    const password = document.getElementById('login-password-input').value;

    if (!email || !password) {
        notify("Por favor, preencha o email e a senha.", true);
        return;
    }

    showScreen('loading');
    try {
        await auth.signInWithEmailAndPassword(email, password);
        // onAuthStateChanged irá tratar da mudança de tela
    } catch (error) {
        console.error("DEBUG: Erro na função handleLogin:", error.code, error.message);
        notify(`Erro no login: As credenciais são inválidas ou o utilizador não existe. (${error.code})`, true);
        showScreen('login');
    }
}

// --- LÓGICA DE REGISTO ---
async function handleSignUp(event) {
    event.preventDefault();
    console.log("Tentativa de registo iniciada...");
    const nome = document.getElementById('signup-nome-input').value;
    const email = document.getElementById('signup-email-input').value;
    const crm = document.getElementById('signup-crm-input').value;
    const especialidade = document.getElementById('signup-especialidade-input').value;
    const password = document.getElementById('signup-password-input').value;

    if (!nome || !email || !crm || !especialidade || !password) {
        notify("Por favor, preencha todos os campos.", true);
        return;
    }

    showScreen('loading');
    try {
        console.log("Passo 1: A criar utilizador no Firebase Auth...");
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        const user = userCredential.user;
        console.log("Passo 1 SUCESSO: Utilizador criado no Firebase Auth com UID:", user.uid);

        console.log("Passo 2: A criar perfil no backend da ShaulaMed...");
        const response_criar_perfil = await fetch(`${API_BASE_URL}/medico/criar_perfil`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uid: user.uid,
                email: email,
                nome_completo: nome,
                apelido: nome.split(' ')[0],
                crm: crm,
                especialidade: especialidade,
                sexo: ""
            })
        });

        if (!response_criar_perfil.ok) {
            const errorData = await response_criar_perfil.json();
            throw new Error(`Falha ao criar perfil no backend: ${errorData.detail}`);
        }
        console.log("Passo 2 SUCESSO: Perfil criado no backend.");

        notify("Conta criada com sucesso! Por favor, faça o login.");
        await auth.signOut();
        showScreen('login');

    } catch (error) {
        console.error("DEBUG: Erro na função handleSignUp:", error.code, error.message);
        notify(`Erro no registo: ${error.message}`, true);
        showScreen('signup');
    }
}

// --- LÓGICA AUXILIAR ---
const showHiddenPass = (passInputId, eyeIconId) => {
    const input = document.getElementById(passInputId);
    const iconEye = document.getElementById(eyeIconId);

    if (input && iconEye) {
        iconEye.addEventListener('click', () => {
            if (input.type === 'password') {
                input.type = 'text';
                iconEye.classList.add('ri-eye-line');
                iconEye.classList.remove('ri-eye-off-line');
            } else {
                input.type = 'password';
                iconEye.classList.remove('ri-eye-line');
                iconEye.classList.add('ri-eye-off-line');
            }
        });
    }
};

// --- INICIALIZAÇÃO DA PÁGINA ---
document.addEventListener('DOMContentLoaded', () => {
    // Inicia mostrando a tela de carregamento
    showScreen('loading');

    // Links para alternar entre formulários
    document.getElementById('show-signup-link').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('signup');
    });
    document.getElementById('show-login-link').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('login');
    });

    // Submissão dos formulários
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignUp);

    // Configuração dos ícones de olho para senha
    showHiddenPass('login-password-input', 'login-eye');
    showHiddenPass('signup-password-input', 'signup-eye');

    // Monitor de estado de autenticação (A LÓGICA PRINCIPAL)
    auth.onAuthStateChanged(async (user) => {
        if (user) {
            currentUser = user;
             try {
                // Ativa a sessão no backend sempre que um utilizador é detectado
                const response_ativar = await fetch(`${API_BASE_URL}/sessao/ativar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ uid: currentUser.uid, email: currentUser.email })
                });
                if (!response_ativar.ok) throw new Error("Falha ao ativar a sessão no backend.");
                showScreen('app');
            } catch(error) {
                console.error(error);
                notify("Não foi possível conectar ao servidor ShaulaMed. Tente novamente.", true);
                await auth.signOut();
                showScreen('login');
            }
        } else {
            // Se não houver utilizador, mostra a tela de login
            currentUser = null;
            showScreen('login');
        }
    });
});