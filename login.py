# login.py

import streamlit as st
import pyrebase
from firebase_config import firebase_config

# Inicializa a conexão com o Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def pagina_login():
    st.title("Bem-vindo(a) ao ShaulaMed")
    st.caption("O seu copiloto clínico com IA reflexiva.")

    # Cria duas abas: uma para Login, outra para Registo
    tab_login, tab_registo = st.tabs(["Login", "Registar"])

    with tab_login:
        st.subheader("Acessar a sua Conta")
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                try:
                    with st.spinner("A autenticar..."):
                        # Tenta fazer o login com o Firebase Authentication
                        utilizador = auth.sign_in_with_email_and_password(email, senha)
                        # Se o login for bem-sucedido, guarda os dados do utilizador na sessão
                        st.session_state.utilizador_logado = utilizador
                        st.rerun() # Recarrega a aplicação
                except Exception as e:
                    st.error("Email ou senha incorretos. Por favor, tente novamente.")
                    st.error(f"Detalhe do erro: {e}")

    with tab_registo:
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            novo_email = st.text_input("Seu Email")
            nova_senha = st.text_input("Crie uma Senha", type="password")
            confirmar_senha = st.text_input("Confirme a Senha", type="password")
            register_button = st.form_submit_button("Registar")

            if register_button:
                if nova_senha == confirmar_senha:
                    try:
                        with st.spinner("A criar a sua conta..."):
                            # Tenta criar um novo utilizador no Firebase Authentication
                            auth.create_user_with_email_and_password(novo_email, nova_senha)
                            st.success("Conta criada com sucesso! Por favor, faça o login na aba ao lado.")
                            st.balloons()
                    except Exception as e:
                        st.error("Não foi possível criar a conta. Este email já pode estar em uso.")
                        st.error(f"Detalhe do erro: {e}")
                else:
                    st.warning("As senhas não coincidem.")