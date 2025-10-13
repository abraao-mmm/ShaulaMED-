// src/firebase/config.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Suas configurações do Firebase
const firebaseConfig = {
    apiKey: "AIzaSyBwzlg3up7Lm1FYPxuBfHx6TFtYPziBBzE",
    authDomain: "shaulamed-mvp.firebaseapp.com",
    projectId: "shaulamed-mvp",
    storageBucket: "shaulamed-mvp.firebasestorage.app",
    messagingSenderId: "1089322609573",
    appId: "1:1089322609573:web:8cd64115a76c03fbb5d64c"
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);

// Exporta o serviço de autenticação para ser usado em outros lugares
export const auth = getAuth(app);