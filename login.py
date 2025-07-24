# login.py (Com Registo Completo)

import streamlit as st
import pyrebase
from firebase_config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
# Precisaremos de uma referência ao Firestore aqui também para criar o perfil
db = firebase.database() # Ou firestore.client() dependendo da sua config

def pagina_login():
    st.title("Bem-vindo(a) ao ShaulaMed")
    st.caption("O seu copiloto clínico com IA reflexiva.")

    tab_login, tab_registo = st.tabs(["Login", "Registar"])

    with tab_login:
        # ... (o formulário de login continua o mesmo)
        pass

    with tab_registo:
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            st.write("Passo 1: Credenciais de Acesso")
            novo_email = st.text_input("Seu Email*")
            nova_senha = st.text_input("Crie uma Senha*", type="password")
            
            st.markdown("---")
            st.write("Passo 2: Perfil Profissional")
            nome_completo = st.text_input("Nome Completo*")
            apelido = st.text_input("Como prefere ser chamado(a)? (ex: Dr. João)")
            crm = st.text_input("CRM*")
            especialidade = st.text_input("Especialidade*")
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"])
            
            register_button = st.form_submit_button("Criar Conta")

            if register_button:
                # Validação simples
                if not novo_email or not nova_senha or not nome_completo or not crm or not especialidade:
                    st.warning("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    try:
                        with st.spinner("A criar a sua conta..."):
                            # 1. Cria o utilizador no Firebase Authentication
                            utilizador = auth.create_user_with_email_and_password(novo_email, nova_senha)
                            
                            # 2. Guarda as informações adicionais no Firestore ou Realtime Database
                            uid = utilizador['localId']
                            dados_medico = {
                                "nome_completo": nome_completo,
                                "apelido": apelido if apelido else nome_completo.split(" ")[0],
                                "crm": crm,
                                "especialidade": especialidade,
                                "sexo": sexo,
                                "email": novo_email
                            }
                            # Cria um novo "documento" para o médico na nossa base de dados
                            # usando o UID da autenticação como ID.
                            db.collection("medicos").document(uid).set(dados_medico)

                            st.success("Conta criada com sucesso! Por favor, faça o login na aba ao lado.")
                            st.balloons()
                    except Exception as e:
                        st.error("Não foi possível criar a conta. Este email já pode estar em uso.")