# login.py (Com Ativação de Sessão no Back-end)

import streamlit as st
import pyrebase
import requests
from firebase_config import firebase_config

API_URL = "https://shaulamed-api.onrender.com" # A URL da sua API

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def pagina_login():
    # ... (o código do título e das abas continua o mesmo)
    tab_login, tab_registo = st.tabs(["Login", "Registar"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                try:
                    with st.spinner("A autenticar..."):
                        # 1. Faz o login no Firebase Authentication
                        utilizador = auth.sign_in_with_email_and_password(email, senha)
                        
                        # --- NOVO PASSO DE ATIVAÇÃO ---
                        # 2. Avisa o nosso back-end para ativar um agente para este utilizador
                        uid = utilizador['localId']
                        requests.post(f"{API_URL}/sessao/ativar", json={"uid": uid, "email": email})
                        
                        # 3. Guarda os dados do utilizador na sessão e recarrega
                        st.session_state.utilizador_logado = utilizador
                        st.rerun()
                except Exception:
                    st.error("Email ou senha incorretos. Por favor, tente novamente.")

    with tab_registo:
        # ... (o código do formulário de registo continua o mesmo e já está correto)
        pass