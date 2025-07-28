# app.py (VERSÃO REATORADA - STATELESS)

import streamlit as st
import requests
import json
import random
from login import pagina_login

# --- CONFIGURAÇÃO DA PÁGINA E URL DA API ---
st.set_page_config(
    page_title="ShaulaMed",
    layout="centered",
    initial_sidebar_state="expanded"
)
# Use a URL da sua API no Render. Garanta que ela não tenha espaços no final.
API_URL = "https://shaulamed-api-1x9x.onrender.com"
# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Consulta"
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
# NOVO: O objeto da consulta agora vive no estado da sessão do front-end
if 'consulta_atual' not in st.session_state:
    st.session_state.consulta_atual = None
if 'ultima_reflexao' not in st.session_state:
    st.session_state.ultima_reflexao = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL ---
def shaulamed_app():
    uid = st.session_state.utilizador_logado.get('localId')
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None
        st.rerun()
        return

    # Estilo CSS (sem alterações)
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #0A0A2A; }
        [data-testid="stSidebar"] { background-color: #1E1E3F; }
        .stButton > button {
            border-radius: 8px; border: 1px solid #8A2BE2;
            background-color: transparent; color: #E0E0E0;
            transition: all 0.2s ease-in-out;
        }
        .stButton > button:hover {
            border-color: #E0E0E0; background-color: #6A1B9A; color: white;
        }
        .stButton > button[kind="primary"] { background-color: #8A2BE2; color: white; }
        .stJson {
            border: 1px solid #8A2BE2 !important;
            box-shadow: 0 0 15px rgba(138, 43, 226, 0.5) !important;
            border-radius: 10px !important;
        }
        .step-active { font-weight: bold; color: #E0E0E0; border-bottom: 2px solid #8A2BE2; padding-bottom: 5px; }
        .step-inactive { color: #555; }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Funções Auxiliares de UI (sem alterações) ---
    FRASES_BOAS_VINDAS = ["Olá. Senti a sua presença. Em que parte da jornada estamos hoje?", "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio."]
    def desenhar_jornada(etapa_atual=1):
        etapas = ["1. Iniciar", "2. Processar", "3. Finalizar"]; cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f'<p class="{"step-active" if (i+1) == etapa_atual else "step-inactive"}">{etapas[i]}</p>', unsafe_allow_html=True)
        st.markdown("---")

    def desenhar_indicador_confianca(nivel):
        try: nivel = float(str(nivel).split(" ")[0].replace(",", "."))
        except: nivel = 0.0
        estrelas_cheias = '★' * int(nivel * 10); estrelas_vazias = '☆' * (10 - int(nivel * 10))
        st.markdown("##### Nível de Confiança da IA"); st.markdown(f"<div style='font-size: 1.2rem; color: #FFD700;'>{estrelas_cheias}<span style='color: #555;'>{estrelas_vazias}</span></div>", unsafe_allow_html=True)

    # --- LÓGICA DAS PÁGINAS (REATORADA) ---
    def pagina_inicial():
        if st.session_state.ultima_reflexao:
            st.success(f"**Reflexão da Shaula:** \"_{st.session_state.ultima_reflexao}_\"")
            st.session_state.ultima_reflexao = None # Limpa a reflexão após mostrar
        else:
            st.info(f"**Shaula:** \"_{random.choice(FRASES_BOAS_VINDAS)}_\"")
        
        desenhar_jornada(1)
        if st.button("▶️ Iniciar Nova Consulta", use_container_width=True):
            with st.spinner("A preparar novo formulário de consulta..."):
                try:
                    # 1. Chama o novo endpoint para obter um objeto de consulta em branco
                    response = requests.post(f"{API_URL}/consulta/iniciar/{uid}", timeout=40)
                    if response.status_code == 200:
                        st.session_state.consulta_atual = response.json() # 2. Armazena no estado da sessão
                        st.session_state.etapa = 2
                        st.rerun()
                    else:
                        st.error(f"O servidor da API respondeu com um erro ({response.status_code}). Detalhe: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}. O servidor pode estar a iniciar. Tente novamente.")

    def pagina_consulta():
        desenhar_jornada(2)
        
        # Guardamos a transcrição para exibir na UI, mesmo que o objeto completo seja complexo
        transcricao_atual = st.session_state.consulta_atual.get('transcricao_consulta', "")

        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("##### Relato do Paciente")
            fala_paciente = st.text_area("Insira a fala do paciente aqui:", height=150, key="fala_texto")
            
            if st.button("Processar Relato", use_container_width=True):
                if fala_paciente:
                    with st.spinner("A processar na nuvem..."):
                        # 1. Prepara o payload com o estado atual da consulta e a nova fala
                        dados = {"consulta_atual": st.session_state.consulta_atual, "fala": {"texto": fala_paciente}}
                        try:
                            response = requests.post(f"{API_URL}/consulta/processar/{uid}", json=dados)
                            if response.status_code == 200:
                                # 2. Atualiza o estado da consulta com a resposta da API
                                st.session_state.consulta_atual = response.json()
                                st.rerun()
                            else:
                                st.error(f"Erro ao processar na API ({response.status_code}): {response.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erro de conexão ao processar: {e}")
                else:
                    st.warning("Por favor, insira o relato do paciente.")

            if transcricao_atual:
                st.info(f"**Relatos Processados:**\n\n\"_{transcricao_atual}_\"")

        with col2:
            st.markdown("##### Sugestão da IA")
            sugestao = st.session_state.consulta_atual.get('sugestao_ia', {})
            if sugestao:
                hipoteses = sugestao.get("hipoteses_diagnosticas", []); conduta = sugestao.get("sugestao_conduta", "N/A"); exames = sugestao.get("exames_sugeridos", []); confianca = sugestao.get("nivel_confianca_ia", 0.0)
                with st.expander("**Hipóteses**", expanded=True): st.write(hipoteses)
                st.markdown("**Conduta Sugerida:**"); st.write(conduta)
                with st.expander("**Exames Sugeridos**"): st.write(exames)
                st.markdown("---"); desenhar_indicador_confianca(confianca)
            else:
                st.info("Aguardando processamento do relato.")
        
        st.markdown("---")
        if st.button("⏹️ Finalizar Consulta", use_container_width=True, type="primary"):
            st.session_state.etapa = 3; st.rerun()

    def pagina_finalizacao():
        desenhar_jornada(3)
        st.info("Revise os dados e insira sua conduta final para registrar o aprendizado da IA.")
        with st.form("finalizar_form"):
            decisao_final = st.text_area("Insira a decisão clínica final:", height=150)
            submitted = st.form_submit_button("Salvar e Concluir Sessão")
            if submitted:
                if decisao_final:
                    with st.spinner("A finalizar, a salvar no banco de dados e a gerar reflexão..."):
                        # 1. Prepara o payload final
                        dados = {"consulta_atual": st.session_state.consulta_atual, "decisao": {"decisao": decisao_final, "resumo": "..."}}
                        try:
                            response = requests.post(f"{API_URL}/consulta/finalizar/{uid}", json=dados)
                            if response.status_code == 200:
                                # 2. Guarda a reflexão para mostrar na próxima tela
                                st.session_state.ultima_reflexao = response.json().get("reflexao")
                                # 3. Limpa o estado e volta para o início
                                st.session_state.etapa = 1
                                st.session_state.consulta_atual = None
                                st.rerun()
                            else:
                                st.error(f"Erro ao finalizar na API ({response.status_code}): {response.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erro de conexão ao finalizar: {e}")
                else:
                    st.warning("Por favor, insira a decisão final.")
    
    # --- ROTEADOR DA INTERFACE ---
    with st.sidebar:
        st.title("🩺 ShaulaMed")
        st.caption(f"Médico: {st.session_state.utilizador_logado.get('email', 'N/A')}")
        if st.button("Sair", use_container_width=True):
            st.session_state.utilizador_logado = None; st.rerun()
    
    st.title("ShaulaMed Copilot")

    if st.session_state.pagina == "Consulta":
        if st.session_state.etapa == 1: pagina_inicial()
        elif st.session_state.etapa == 2: pagina_consulta()
        elif st.session_state.etapa == 3: pagina_finalizacao()

# --- ROUTER PRINCIPAL (Verifica se está logado) ---
if st.session_state.utilizador_logado:
    shaulamed_app()
else:
    pagina_login()