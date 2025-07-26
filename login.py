# login.py

import streamlit as st
import pyrebase
import requests
from firebase_config import firebase_config

API_URL = "https://shaulamed-api.onrender.com" 

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def pagina_login():
    st.title("Bem-vindo(a) ao ShaulaMed")
    tab_login, tab_registo = st.tabs(["Login", "Registar"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Login")
            if login_button:
                try:
                    with st.spinner("A autenticar..."):
                        utilizador = auth.sign_in_with_email_and_password(email, senha)
                        uid = utilizador['localId']
                        # Avisa o back-end para ativar a sessão
                        response_ativar = requests.post(f"{API_URL}/sessao/ativar", json={"uid": uid, "email": email})
                        if response_ativar.status_code != 200:
                            st.error("Autenticado com sucesso, mas falha ao ativar a sessão no servidor.")
                            return
                        st.session_state.utilizador_logado = utilizador
                        st.rerun()
                except Exception:
                    st.error("Email ou senha incorretos.")

    with tab_registo:
        with st.form("register_form"):
            # ... (seus campos de formulário aqui)
            novo_email = st.text_input("Seu Email*", key="reg_email")
            nova_senha = st.text_input("Crie uma Senha*", type="password", key="reg_senha1")
            nome_completo = st.text_input("Nome Completo*")
            apelido = st.text_input("Como prefere ser chamado(a)?")
            crm = st.text_input("CRM*")
            especialidade = st.selectbox("Especialidade*", ["Otorrinolaringologia"])
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
            
            register_button = st.form_submit_button("Criar Conta")

            if register_button:
                # ... (validações)
                try:
                    with st.spinner("A criar a sua conta..."):
                        utilizador = auth.create_user_with_email_and_password(novo_email, nova_senha)
                        uid = utilizador['localId']
                        dados_perfil = {
                            "uid": uid, "email": novo_email, "nome_completo": nome_completo,
                            "apelido": apelido if apelido else nome_completo.split(" ")[0],
                            "crm": crm, "especialidade": especialidade, "sexo": sexo
                        }
                        response = requests.post(f"{API_URL}/medico/criar_perfil", json=dados_perfil)
                        if response.status_code == 200:
                            st.success("Conta criada com sucesso! Por favor, faça o login.")
                            st.balloons()
                        else:
                            st.error("Erro ao criar o perfil na base de dados.")
                            st.error(f"Detalhe do Servidor: {response.text}")
                except Exception as e:
                    st.error(f"Não foi possível criar a conta. O email já pode estar em uso.")