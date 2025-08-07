// app.js

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const firebaseConfig = {
    apiKey: "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE", // Sua chave de API
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
const signupContainer = document.getElementById('signup-container'); // Novo
const mainContainer = document.querySelector('.main-container');

// --- FUNÇÕES DE UI ---
function showScreen(screen) {
    loadingContainer.style.display = 'none';
    loginContainer.style.display = 'none';
    signupContainer.style.display = 'none';
    mainContainer.style.display = 'none';

    if (screen === 'login') loginContainer.style.display = 'grid';
    if (screen === 'signup') signupContainer.style.display = 'grid';
    if (screen === 'app') mainContainer.style.display = 'block';
    if (screen === 'loading') loadingContainer.style.display = 'flex';
}

function notify(message, isError = false) {
    // Implementação simples de notificação, pode ser melhorada com uma biblioteca
    alert(message); 
}


// --- LÓGICA DE LOGIN ---
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email-input').value;
    const password = document.getElementById('login-password-input').value;

    if (!email || !password) {
        notify("Por favor, preencha o email e a senha.", true);
        return;
    }

    showScreen('loading');
    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        // A transição para a tela do app será feita pelo onAuthStateChanged
    } catch (error) {
        console.error("Erro no login:", error);
        notify(`Erro no login: ${error.message}`, true);
        showScreen('login');
    }
}

// --- LÓGICA DE REGISTO (NOVO) ---
async function handleSignUp(event) {
    event.preventDefault();
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
        // Passo 1: Criar o utilizador no Firebase Authentication
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        const user = userCredential.user;

        // Passo 2: Enviar os dados do perfil para a sua API para salvar no Firestore
        const response_criar_perfil = await fetch(`${API_BASE_URL}/medico/criar_perfil`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                uid: user.uid,
                email: email,
                nome_completo: nome,
                apelido: nome.split(' ')[0], // Usa o primeiro nome como apelido
                crm: crm,
                especialidade: especialidade,
                sexo: "" // Pode ser adicionado um campo para isso se desejar
            })
        });

        if (!response_criar_perfil.ok) {
            // Se falhar aqui, o utilizador foi criado no Auth mas não no Firestore.
            // Idealmente, deveria haver um tratamento para isso.
            const errorData = await response_criar_perfil.json();
            throw new Error(`Falha ao criar perfil no backend: ${errorData.detail}`);
        }

        notify("Conta criada com sucesso! Por favor, faça o login.");
        await auth.signOut(); // Força o logout para que o utilizador precise logar
        showScreen('login');

    } catch (error) {
        console.error("Erro no registo:", error);
        notify(`Erro no registo: ${error.message}`, true);
        showScreen('signup');
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

    // Monitor de estado de autenticação
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
            currentUser = null;
            showScreen('login');// app.js (Versão com depuração melhorada)

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "https://shaulamed-api-1x9x.onrender.com";

const firebaseConfig = {
    apiKey: "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE", // GARANTA QUE ESTA CONFIG ESTÁ 100% CORRETA
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
    loadingContainer.style.display = 'none';
    loginContainer.style.display = 'none';
    signupContainer.style.display = 'none';
    mainContainer.style.display = 'none';

    if (screen === 'login') loginContainer.style.display = 'grid';
    if (screen === 'signup') signupContainer.style.display = 'grid';
    if (screen === 'app') mainContainer.style.display = 'block';
    if (screen === 'loading') loadingContainer.style.display = 'flex';
}

function notify(message, isError = false) {
    alert(message); 
}

// --- LÓGICA DE LOGIN ---
async function handleLogin(event) {
    event.preventDefault();
    console.log("Tentativa de login iniciada..."); // Log de depuração
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
    console.log("Tentativa de registo iniciada..."); // Log de depuração
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

// ... (O resto do ficheiro 'app.js' permanece o mesmo)
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

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('show-signup-link').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('signup');
    });
    document.getElementById('show-login-link').addEventListener('click', (e) => {
        e.preventDefault();
        showScreen('login');
    });

    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignUp);

    showHiddenPass('login-password-input', 'login-eye');
    showHiddenPass('signup-password-input', 'signup-eye');

    auth.onAuthStateChanged(async (user) => {
        if (user) {
            currentUser = user;
             try {
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
            currentUser = null;
            showScreen('login');
        }
    });
});
        }
    });
});