// app.js

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

// Cole aqui as credenciais do seu projeto Firebase (as mesmas do firebase_config.py)
const firebaseConfig = {
    "apiKey": "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE",
    "authDomain": "shaulamed-mvp.firebaseapp.com",
    "projectId": "shaulamed-mvp", 
    "storageBucket": "shaulamed-mvp.firebasestorage.app",
    "messagingSenderId": "1089322609573",
    "appId": "1089322609573:web:8cd64115a76c03fbb5d64c",
    "databaseURL": ""
};

// --- INICIALIZAÇÃO DO FIREBASE ---
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// --- GERENCIAMENTO DE ESTADO ---
let currentUser = null;

// --- FUNÇÕES PRINCIPAIS ---

function showLoginScreen() {
    document.getElementById('login-container').style.display = 'flex';
    document.querySelector('.main-container').style.display = 'none';
}

function showAppScreen() {
    document.getElementById('login-container').style.display = 'none';
    document.querySelector('.main-container').style.display = 'block';
}

async function handleLogin() {
    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;

    if (!email || !password) {
        alert("Por favor, preencha o email e a senha.");
        return;
    }

    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        currentUser = userCredential.user;
        console.log("Login bem-sucedido:", currentUser.uid);
        
        // Ativa a sessão no backend
        const response_ativar = await fetch(`${API_BASE_URL}/sessao/ativar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid: currentUser.uid, email: currentUser.email })
        });
        
        if (!response_ativar.ok) {
            throw new Error("Falha ao ativar a sessão no backend.");
        }
        
        console.log("Sessão ativada no backend com sucesso.");
        showAppScreen();

    } catch (error) {
        console.error("Erro no login:", error);
        alert(`Erro no login: ${error.message}`);
    }
}

// --- INICIALIZAÇÃO DA PÁGINA ---
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    loginButton.addEventListener('click', handleLogin);

    // Verifica se o usuário já está logado na sessão do navegador
    auth.onAuthStateChanged(user => {
        if (user) {
            console.log("Usuário já está logado, a mostrar a aplicação.");
            currentUser = user;
            showAppScreen();
        } else {
            console.log("Nenhum usuário logado, a mostrar a tela de login.");
            showLoginScreen();
        }
    });
});