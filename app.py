# app.py (Versão 2.0 - Com Autenticação)

import streamlit as st
import requests
import json
import random
from streamlit_mic_recorder import mic_recorder
from transcritor import transcrever_audio_bytes
from login import pagina_login # Importa a nossa nova página de login

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# Verifica se a informação do utilizador logado já existe na sessão
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL (SHAULAMED) ---
# Todo o nosso código antigo do ShaulaMed agora vive dentro desta função
def shaulamed_app():
    API_URL = "https://shaulamed-api.onrender.com" # A URL da sua API no Render

    # Configuração da Página e Estilo
    st.set_page_config(page_title="ShaulaMed Copilot", layout="centered", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
        .stJson { border: 1px solid #8A2BE2 !important; box-shadow: 0 0 15px rgba(138, 43, 226, 0.5) !important; border-radius: 10px !important; }
        .step-active { font-weight: bold; color: #E0E0E0; border-bottom: 2px solid #8A2BE2; padding-bottom: 5px; }
        .step-inactive { color: #555; }
    </style>
    """, unsafe_allow_html=True)

    # Inicialização do estado da sessão específico da aplicação
    if 'pagina' not in st.session_state: st.session_state.pagina = "Consulta"
    if 'etapa' not in st.session_state: st.session_state.etapa = 1
    if 'sugestao' not in st.session_state: st.session_state.sugestao = None
    if 'texto_transcrito' not in st.session_state: st.session_state.texto_transcrito = ""

    # Listas de Frases
    FRASES_BOAS_VINDAS = [
        "Olá. Senti a sua presença. Em que parte da jornada estamos hoje?",
        "Os seus pensamentos formam constelações. Vamos explorá-las juntos?",
        "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio."
    ]

    # Funções Auxiliares de Interface
    def desenhar_jornada(etapa_atual=1):
        etapas = ["1. Iniciar", "2. Ouvir & Processar", "3. Finalizar"]
        cols = st.columns(3); st.markdown("---")

    def desenhar_indicador_confianca(nivel: float):
        if not isinstance(nivel, (float, int)):
            try: nivel = float(str(nivel).split(" ")[0].replace(",", "."))
            except (ValueError, IndexError): nivel = 0.0
        estrelas_preenchidas = int(nivel * 10); estrelas_vazias = 10 - estrelas_preenchidas
        display_html = f"<div style='font-size: 1.2rem; color: #FFD700;'>{'★' * estrelas_preenchidas}<span style='color: #555;'>{'☆' * estrelas_vazias}</span></div>"
        st.markdown("##### Nível de Confiança da IA"); st.markdown(display_html, unsafe_allow_html=True)

    # Funções de Página
    def pagina_inicial():
        if 'ultima_reflexao' in st.session_state and st.session_state.ultima_reflexao:
            st.success(f"**Reflexão da Shaula:** \"_{st.session_state.ultima_reflexao}_\"")
            del st.session_state.ultima_reflexao
        else:
            st.info(f"**Shaula:** \"_{random.choice(FRASES_BOAS_VINDAS)}_\"")
        desenhar_jornada(1)
        if st.button("▶️ Iniciar Nova Consulta", type="primary"):
            with st.spinner("A conectar com o servidor da API..."):
                try:
                    response = requests.post(f"{API_URL}/consulta/iniciar", timeout=30)
                    if response.status_code == 200: st.session_state.etapa = 2; st.rerun()
                    else: st.error(f"O servidor da API respondeu com um erro ({response.status_code}).")
                except requests.exceptions.RequestException as e: st.error(f"Erro de conexão: {e}")

    def pagina_consulta():
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            audio_gravado = mic_recorder(start_prompt="🎙️ Gravar Fala", stop_prompt="⏹️ Parar", key='recorder')
            if audio_gravado:
                st.session_state.audio_gravado = audio_gravado['bytes']; st.audio(audio_gravado['bytes'])
            if 'audio_gravado' in st.session_state and st.session_state.audio_gravado:
                if st.button("Processar Áudio"):
                    with st.spinner("A transcrever e a processar..."):
                        texto = transcrever_audio_bytes(st.session_state.audio_gravado)
                        if texto:
                            st.session_state.texto_transcrito = texto
                            response = requests.post(f"{API_URL}/consulta/processar", json={"texto": texto})
                            if response.status_code == 200: st.session_state.sugestao = response.json().get("sugestao")
                            else: st.error("Erro ao processar.")
                        else: st.warning("Não foi possível transcrever.")
                        st.session_state.audio_gravado = None; st.rerun()
            if st.session_state.texto_transcrito: st.info(f"**Última Transcrição:** \"_{st.session_state.texto_transcrito}_\"")
        with col2:
            st.markdown("##### Sugestão da IA")
            if st.session_state.sugestao:
                sugestao = st.session_state.sugestao; hipoteses = sugestao.get("hipoteses_diagnosticas", []); conduta = sugestao.get("sugestao_conduta", "N/A"); exames = sugestao.get("exames_sugeridos", []); confianca = sugestao.get("nivel_confianca_ia", 0.0)
                with st.expander("**Hipóteses**", expanded=True): st.write(hipoteses)
                st.markdown("**Conduta Sugerida:**"); st.write(conduta)
                with st.expander("**Exames Sugeridos**"): st.write(exames)
                st.markdown("---"); desenhar_indicador_confianca(confianca)
            else: st.info("Aguardando processamento...")
        if st.button("⏹️ Finalizar Consulta"): st.session_state.etapa = 3; st.rerun()

    def pagina_finalizacao():
        desenhar_jornada(3)
        with st.form("finalizar_form"):
            decisao_final = st.text_area("Insira a decisão clínica final:")
            submitted = st.form_submit_button("Salvar e Concluir Sessão")
            if submitted:
                if decisao_final:
                    with st.spinner("A finalizar e a gerar reflexão..."):
                        dados = {"decisao": decisao_final, "resumo": "..."}
                        response = requests.post(f"{API_URL}/consulta/finalizar", json=dados)
                        if response.status_code == 200:
                            st.session_state.ultima_reflexao = response.json().get("reflexao")
                        st.session_state.etapa = 1; st.rerun()
                else: st.warning("Por favor, insira a decisão final.")
    
    def pagina_relatorio():
        st.header("Painel Reflexivo")
        if st.button("Gerar Relatório", type="primary"):
            with st.spinner("A IA está a refletir..."):
                response = requests.get(f"{API_URL}/relatorio")
                if response.status_code == 200: st.session_state.relatorio_gerado = response.json().get("relatorio")
                else: st.error("Não foi possível gerar.")
        if 'relatorio_gerado' in st.session_state: st.markdown("---"); st.markdown(st.session_state.relatorio_gerado)

    # Lógica de Navegação da Aplicação Principal
    with st.sidebar:
        st.title("🩺 ShaulaMed")
        if 'utilizador_logado' in st.session_state and st.session_state.utilizador_logado is not None:
             st.caption(f"Médico: {st.session_state.utilizador_logado.get('email', '')}")
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
    # Se o utilizador está logado, mostra a aplicação principal
    shaulamed_app()
else:
    # Se não está logado, mostra a página de login
    pagina_login()