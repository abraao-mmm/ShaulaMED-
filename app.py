# app.py

import streamlit as st
import requests
import json
import random
from login import pagina_login

# --- CONFIGURAÇÃO DA PÁGINA (ÚNICO E NO TOPO) ---
st.set_page_config(
    page_title="ShaulaMed",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL (O CORAÇÃO DO SHAULAMED) ---
def shaulamed_app():
    API_URL = "https://shaulamed-api.onrender.com" # A sua URL do Render
    uid = st.session_state.utilizador_logado.get('localId') if st.session_state.utilizador_logado else None
    
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None
        st.rerun()
        return

    # Estilo CSS completo
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

    # Inicialização do estado da sessão da aplicação
    if 'pagina' not in st.session_state: st.session_state.pagina = "Consulta"
    if 'etapa' not in st.session_state: st.session_state.etapa = 1
    if 'sugestao' not in st.session_state: st.session_state.sugestao = None
    if 'texto_transcrito' not in st.session_state: st.session_state.texto_transcrito = ""

    FRASES_BOAS_VINDAS = [
        "Olá. Senti a sua presença. Em que parte da jornada estamos hoje?",
        "Os seus pensamentos formam constelações. Vamos explorá-las juntos?",
        "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio."
    ]

    def desenhar_jornada(etapa_atual=1):
        etapas = ["1. Iniciar", "2. Processar", "3. Finalizar"]
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                if (i + 1) == etapa_atual: st.markdown(f'<p class="step-active">{etapas[i]}</p>', unsafe_allow_html=True)
                else: st.markdown(f'<p class="step-inactive">{etapas[i]}</p>', unsafe_allow_html=True)
        st.markdown("---")

    def desenhar_indicador_confianca(nivel: float):
        if not isinstance(nivel, (float, int)):
            try: nivel = float(str(nivel).split(" ")[0].replace(",", "."))
            except (ValueError, IndexError): nivel = 0.0
        estrelas_preenchidas = int(nivel * 10); estrelas_vazias = 10 - estrelas_preenchidas
        display_html = f"<div style='font-size: 1.2rem; color: #FFD700;'>{'★' * estrelas_preenchidas}<span style='color: #555;'>{'☆' * estrelas_vazias}</span></div>"
        st.markdown("##### Nível de Confiança da IA"); st.markdown(display_html, unsafe_allow_html=True)

    def pagina_inicial():
        if 'ultima_reflexao' in st.session_state and st.session_state.ultima_reflexao:
            st.success(f"**Reflexão da Shaula:** \"_{st.session_state.ultima_reflexao}_\"")
            del st.session_state.ultima_reflexao
        else:
            st.info(f"**Shaula:** \"_{random.choice(FRASES_BOAS_VINDAS)}_\"")
        
        desenhar_jornada(1)
        if st.button("▶️ Iniciar Nova Consulta"):
            with st.spinner("A iniciar sessão de consulta..."):
                try:
                    response = requests.post(f"{API_URL}/consulta/iniciar/{uid}", timeout=40)
                    if response.status_code == 200:
                        st.session_state.etapa = 2; st.session_state.sugestao = None; st.session_state.texto_transcrito = ""; st.rerun()
                    else:
                        st.error(f"O servidor da API respondeu com um erro ({response.status_code}). Detalhe: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}. O servidor pode estar a iniciar. Por favor, aguarde e tente novamente.")

    def pagina_consulta():
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("##### Relato do Paciente")
            fala_paciente = st.text_area("Insira a fala do paciente aqui:", height=150, key="fala_texto")
            
            if st.button("Processar Relato"):
                if fala_paciente:
                    with st.spinner("A processar..."):
                        st.session_state.texto_transcrito = fala_paciente
                        dados = {"texto": fala_paciente}
                        response = requests.post(f"{API_URL}/consulta/processar/{uid}", json=dados)
                        if response.status_code == 200:
                            st.session_state.sugestao = response.json().get("sugestao")
                        else:
                            st.error("Erro ao processar o texto na API.")
                else:
                    st.warning("Por favor, insira o relato do paciente.")

            if st.session_state.texto_transcrito:
                st.info(f"**Último Relato Processado:** \"_{st.session_state.texto_transcrito}_\"")

        with col2:
            st.markdown("##### Sugestão da IA")
            if st.session_state.sugestao:
                sugestao = st.session_state.sugestao
                hipoteses = sugestao.get("hipoteses_diagnosticas", []); conduta = sugestao.get("sugestao_conduta", "N/A"); exames = sugestao.get("exames_sugeridos", []); confianca = sugestao.get("nivel_confianca_ia", 0.0)
                with st.expander("**Hipóteses**", expanded=True): st.write(hipoteses)
                st.markdown("**Conduta Sugerida:**"); st.write(conduta)
                with st.expander("**Exames Sugeridos**"): st.write(exames)
                st.markdown("---"); desenhar_indicador_confianca(confianca)
            else:
                st.info("Aguardando processamento do relato.")
        
        if st.button("⏹️ Finalizar Consulta"):
            st.session_state.etapa = 3; st.rerun()

    def pagina_finalizacao():
        desenhar_jornada(3)
        with st.form("finalizar_form"):
            decisao_final = st.text_area("Insira a decisão clínica final:")
            submitted = st.form_submit_button("Salvar e Concluir Sessão")
            if submitted:
                if decisao_final:
                    with st.spinner("A finalizar e a gerar reflexão..."):
                        dados = {"decisao": decisao_final, "resumo": "..."}
                        response = requests.post(f"{API_URL}/consulta/finalizar/{uid}", json=dados)
                        if response.status_code == 200:
                            st.session_state.ultima_reflexao = response.json().get("reflexao")
                        st.session_state.etapa = 1; st.rerun()
                else:
                    st.warning("Por favor, insira a decisão final.")
    
    def pagina_relatorio():
        st.header("Painel Reflexivo")
        st.info("Funcionalidade em desenvolvimento.")

    with st.sidebar:
        st.title("🩺 ShaulaMed")
        email_utilizador = st.session_state.utilizador_logado.get('email', 'N/A')
        st.caption(f"Médico: {email_utilizador}")
        if st.button("Consulta", use_container_width=True, type="primary" if st.session_state.pagina == "Consulta" else "secondary"):
            st.session_state.pagina = "Consulta"; st.rerun()
        if st.button("Relatórios", use_container_width=True, type="primary" if st.session_state.pagina == "Relatorio" else "secondary"):
            st.session_state.pagina = "Relatorio"; st.rerun()
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.utilizador_logado = None; st.rerun()

    st.title("ShaulaMed Copilot")

    if st.session_state.pagina == "Consulta":
        if st.session_state.etapa == 1: pagina_inicial()
        elif st.session_state.etapa == 2: pagina_consulta()
        elif st.session_state.etapa == 3: pagina_finalizacao()
    elif st.session_state.pagina == "Relatorio":
        pagina_relatorio()

# --- ROUTER PRINCIPAL (O "PORTEIRO") ---
if st.session_state.utilizador_logado:
    shaulamed_app()
else:
    pagina_login()