# login.py

import streamlit as st
import pyrebase
import requests
from firebase_config import firebase_config

# A URL da sua API no Render
API_URL = "https://shaulamed-api.onrender.com" 

# Inicializa a conexão com o Firebase para autenticação
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    st.error(f"Erro ao inicializar o Firebase. Verifique o seu ficheiro firebase_config.py: {e}")
    st.stop()

def pagina_login():
    st.title("Bem-vindo(a) ao ShaulaMed")
    st.caption("O seu copiloto clínico com IA reflexiva.")

    # Cria as duas abas para o utilizador escolher entre Login e Registo
    tab_login, tab_registo = st.tabs(["Login", "Registar"])

    with tab_login:
        st.subheader("Acessar a sua Conta")
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                try:
                    with st.spinner("A autenticar e a ativar a sua sessão... Isto pode demorar até 40 segundos na primeira vez."):
                        # 1. Faz o login no Firebase Authentication
                        utilizador = auth.sign_in_with_email_and_password(email, senha)
                        uid = utilizador['localId']
                        
                        # 2. Avisa o nosso back-end para carregar o perfil e ativar um agente
                        response_ativar = requests.post(f"{API_URL}/sessao/ativar", json={"uid": uid, "email": email}, timeout=40)
                        
                        # 3. Verifica se o back-end respondeu corretamente
                        if response_ativar.status_code == 200:
                            st.session_state.utilizador_logado = utilizador
                            st.rerun()
                        else:
                            st.error(f"Autenticado com sucesso, mas falha ao ativar a sessão no servidor. Detalhe: {response_ativar.text}")

                except requests.exceptions.RequestException as e:
                     st.error(f"Erro de conexão com a API: {e}. O servidor pode estar a iniciar. Por favor, tente novamente em 30 segundos.")
                except Exception:
                    st.error("Email ou senha incorretos. Por favor, tente novamente.")

    with tab_registo:
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            st.write("Passo 1: Credenciais de Acesso")
            novo_email = st.text_input("Seu Email*", key="reg_email")
            nova_senha = st.text_input("Crie uma Senha*", type="password", key="reg_senha1")
            confirmar_senha = st.text_input("Confirme a Senha*", type="password", key="reg_senha2")
            
            st.markdown("---")
            st.write("Passo 2: Perfil Profissional")
            nome_completo = st.text_input("Nome Completo*")
            apelido = st.text_input("Como prefere ser chamado(a)? (ex: Dr. João)")
            crm = st.text_input("CRM*")
            especialidade = st.selectbox("Especialidade*", ["Otorrinolaringologia"])
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"])
            
            register_button = st.form_submit_button("Criar Conta")

            if register_button:
                if not all([novo_email, nova_senha, confirmar_senha, nome_completo, crm, especialidade]):
                    st.warning("Por favor, preencha todos os campos obrigatórios (*).")
                elif nova_senha != confirmar_senha:
                    st.warning("As senhas não coincidem.")
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
                                st.success("Conta criada com sucesso! Por favor, vá para a aba 'Login' para entrar.")
                                st.balloons()
                            else:
                                st.error("Erro ao criar o perfil na base de dados.")
                                st.error(f"Detalhe do Servidor: {response.text}")

                    except Exception as e:
                        # Tenta extrair a mensagem de erro específica do Firebase
                        try:
                            erro_json = json.loads(e.args[1])
                            mensagem_erro = erro_json['error']['message']
                            if "EMAIL_EXISTS" in mensagem_erro:
                                st.error("Não foi possível criar a conta. Este email já está a ser utilizado.")
                            else:
                                st.error(f"Não foi possível criar a conta: {mensagem_erro}")
                        except:
                            st.error("Não foi possível criar a conta. Verifique os seus dados.")