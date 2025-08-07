// app.js

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const firebaseConfig = {
    apiKey: "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE",
    authDomain: "shaulamed-mvp.firebaseapp.com",
    projectId: "shaulamed-mvp",
    storageBucket: "shaulamed-mvp.firebasestorage.app",
    messagingSenderId: "1089322609573",
    appId: "1:1089322609573:web:8cd64115a76c03fbb5d64c"
};

// --- GERENCIAMENTO DE ESTADO ---
let currentUser = null;

// --- ELEMENTOS DA UI ---
const loadingContainer = document.getElementById('loading-container');
const loadingSpinner = document.getElementById('loading-spinner');
const loadingText = document.getElementById('loading-text');
const loginContainer = document.getElementById('login-container');
const mainContainer = document.querySelector('.main-container');

// --- FUNÇÕES DE UI ---
function showLoginScreen() {
    if(loadingContainer) loadingContainer.style.display = 'none';
    if(mainContainer) mainContainer.style.display = 'none';
    if(loginContainer) loginContainer.style.display = 'grid';
}

function showAppScreen() {
    if(loadingContainer) loadingContainer.style.display = 'none';
    if(loginContainer) loginContainer.style.display = 'none';
    if(mainContainer) mainContainer.style.display = 'block';
}

// --- LÓGICA DE LOGIN ---
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;

    if (!email || !password) {
        alert("Por favor, preencha o email e a senha.");
        return;
    }

    try {
        const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
        currentUser = userCredential.user;
        
        const response_ativar = await fetch(`${API_BASE_URL}/sessao/ativar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: currentUser.uid, email: currentUser.email })
        });
        
        if (!response_ativar.ok) throw new Error("Falha ao ativar a sessão no backend.");
        
    } catch (error) {
        console.error("Erro no login:", error);
        alert(`Erro no login: ${error.message}`);
    }
}

// --- MOSTRAR/ESCONDER SENHA ---
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
    try {
        // Inicializa o Firebase
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();

        // Anexa os eventos
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
        }
        showHiddenPass('password-input', 'login-eye');

        // Configura o observador de autenticação
        auth.onAuthStateChanged(user => {
            if (user) {
                currentUser = user;
                showAppScreen();
            } else {
                currentUser = null;
                showLoginScreen();
            }
        });

    } catch (error) {
        // Se a inicialização do Firebase falhar, mostra uma mensagem de erro
        console.error("Erro Crítico ao Inicializar o Firebase:", error);
        if(loadingSpinner) loadingSpinner.style.display = 'none';
        if(loadingText) loadingText.textContent = 'Erro ao conectar. Verifique sua conexão e atualize a página.';
    }
});