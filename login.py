# login.py (Com Registo via API e Selectbox)

import streamlit as st
import pyrebase
import requests
from firebase_config import firebase_config

API_URL = "https://shaulamed-api.onrender.com" # A URL da sua API

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def pagina_login():
    st.title("Bem-vindo(a) ao ShaulaMed")
    st.caption("O seu copiloto clínico com IA reflexiva.")

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
                        utilizador = auth.sign_in_with_email_and_password(email, senha)
                        st.session_state.utilizador_logado = utilizador
                        st.rerun()
                except Exception:
                    st.error("Email ou senha incorretos. Por favor, tente novamente.")

    with tab_registo:
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            st.write("Passo 1: Credenciais de Acesso")
            novo_email = st.text_input("Seu Email*")
            nova_senha = st.text_input("Crie uma Senha*", type="password")
            
            st.markdown("---")
            st.write("Passo 2: Perfil Profissional")
            nome_completo = st.text_input("Nome Completo*")
            apelido = st.text_input("Como prefere ser chamado(a)?")
            crm = st.text_input("CRM*")
            
            # --- CAMPO DE ESPECIALIDADE ATUALIZADO ---
            especialidade = st.selectbox("Especialidade*", ["Otorrinolaringologia"])
            
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"])
            
            register_button = st.form_submit_button("Criar Conta")

            if register_button:
                if not all([novo_email, nova_senha, nome_completo, crm, especialidade]):
                    st.warning("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    try:
                        with st.spinner("A criar a sua conta..."):
                            # 1. Cria o utilizador no Firebase Authentication
                            utilizador = auth.create_user_with_email_and_password(novo_email, nova_senha)
                            uid = utilizador['localId']
                            
                            # 2. Prepara os dados do perfil para enviar à API
                            dados_perfil = {
                                "uid": uid, "email": novo_email, "nome_completo": nome_completo,
                                "apelido": apelido if apelido else nome_completo.split(" ")[0],
                                "crm": crm, "especialidade": especialidade, "sexo": sexo
                            }
                            
                            # 3. Pede à nossa API para criar o perfil no Firestore
                            response = requests.post(f"{API_URL}/medico/criar_perfil", json=dados_perfil)
                            
                            if response.status_code == 200:
                                st.success("Conta criada com sucesso! Por favor, faça o login na aba ao lado.")
                                st.balloons()
                            else:
                                st.error("Erro ao criar o perfil na base de dados. Tente novamente.")
                                st.error(f"Detalhe: {response.text}")

                    except Exception as e:
                        st.error("Não foi possível criar a conta. Este email já pode estar em uso.")