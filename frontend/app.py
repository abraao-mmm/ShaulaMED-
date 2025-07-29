# app.py (Versão com Gravador Contínuo - Fase 1 do Modo Ambiente)

import streamlit as st
import requests
import json
import random
import pandas as pd
from login import pagina_login
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÃO DA PÁGINA E URL DA API ---
st.set_page_config(
    page_title="ShaulaMed",
    layout="centered",
    initial_sidebar_state="expanded"
)
API_URL = "https://shaulamed-api-1x9x.onrender.com"

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Consulta"
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'consulta_atual' not in st.session_state:
    st.session_state.consulta_atual = None
if 'ultima_reflexao' not in st.session_state:
    st.session_state.ultima_reflexao = None
# NOVO: Controla se estamos no modo de escuta ativa
if "escutando" not in st.session_state:
    st.session_state.escutando = False


# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL ---
def shaulamed_app():
    uid = st.session_state.utilizador_logado.get('localId')
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente."); st.session_state.utilizador_logado = None; st.rerun(); return

    # Estilo CSS (sem alterações)
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #0A0A2A; }
        [data-testid="stSidebar"] { background-color: #1E1E3F; }
        .stButton > button { border-radius: 8px; border: 1px solid #8A2BE2; background-color: transparent; color: #E0E0E0; transition: all 0.2s ease-in-out; }
        .stButton > button:hover { border-color: #E0E0E0; background-color: #6A1B9A; color: white; }
        .stButton > button[kind="primary"] { background-color: #8A2BE2; color: white; }
        .step-active { font-weight: bold; color: #E0E0E0; border-bottom: 2px solid #8A2BE2; padding-bottom: 5px; }
        .step-inactive { color: #555; }
        .report-box { background-color: #1E1E3F; border-left: 5px solid #8A2BE2; padding: 20px; border-radius: 8px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    FRASES_BOAS_VINDAS = ["Olá. Senti a sua presença. Em que parte da jornada estamos hoje?", "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio."]

    def desenhar_jornada(etapa_atual=1):
        etapas = ["1. Iniciar", "2. Processar", "3. Finalizar"]; cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f'<p class="{"step-active" if (i+1) == etapa_atual else "step-inactive"}">{etapas[i]}</p>', unsafe_allow_html=True)
        st.markdown("---")

    def desenhar_indicador_confianca(nivel: float):
        if not isinstance(nivel, (float, int)):
            try: nivel = float(str(nivel).split(" ")[0].replace(",", "."))
            except: nivel = 0.0
        estrelas_preenchidas = int(nivel * 10); estrelas_vazias = 10 - estrelas_preenchidas
        display_html = f"<div style='font-size: 1.2rem; color: #FFD700;'>{'★' * estrelas_preenchidas}<span style='color: #555;'>{'☆' * estrelas_vazias}</span></div>"
        st.markdown("##### Nível de Confiança da IA"); st.markdown(display_html, unsafe_allow_html=True)

    def pagina_inicial():
        if st.session_state.ultima_reflexao:
            st.success(f"**Reflexão da Shaula:** \"_{st.session_state.ultima_reflexao}_\"")
            st.session_state.ultima_reflexao = None
        else:
            st.info(f"**Shaula:** \"_{random.choice(FRASES_BOAS_VINDAS)}_\"")
        
        desenhar_jornada(1)
        if st.button("▶️ Iniciar Nova Consulta", use_container_width=True):
            with st.spinner("A iniciar sessão de consulta..."):
                try:
                    response = requests.post(f"{API_URL}/consulta/iniciar/{uid}", timeout=40)
                    if response.status_code == 200:
                        st.session_state.consulta_atual = response.json()
                        st.session_state.etapa = 2
                        st.session_state.escutando = False
                        st.rerun()
                    else:
                        st.error(f"O servidor da API respondeu com um erro ({response.status_code}). Detalhe: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}.")

    def pagina_consulta():
        desenhar_jornada(2)
        transcricao_atual = st.session_state.consulta_atual.get('transcricao_consulta', "")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("##### Captura da Consulta")

            # --- LÓGICA DO GRAVADOR CONTÍNUO ---
            if not st.session_state.escutando:
                if st.button("▶️ Iniciar Escuta", use_container_width=True):
                    st.session_state.escutando = True
                    st.rerun()
            else:
                st.info("Shaula está a escutar... Clique em 'Parar' quando o relato principal terminar.")
                audio_info = mic_recorder(
                    start_prompt="🔴 A Gravar...",
                    stop_prompt="⏹️ Parar Escuta",
                    key='recorder'
                )
                if audio_info and audio_info['bytes']:
                    st.session_state.escutando = False
                    audio_bytes = audio_info['bytes']
                    with st.spinner("A transcrever e a analisar a consulta..."):
                        try:
                            files = {'ficheiro_audio': ("audio.wav", audio_bytes, "audio/wav")}
                            response_transcricao = requests.post(f"{API_URL}/audio/transcrever", files=files, timeout=90)
                            if response_transcricao.status_code == 200:
                                texto_transcrito = response_transcricao.json().get("texto_transcrito", "")
                                if texto_transcrito:
                                    dados = {"consulta_atual": st.session_state.consulta_atual, "fala": {"texto": texto_transcrito}}
                                    response_proc = requests.post(f"{API_URL}/consulta/processar/{uid}", json=dados)
                                    if response_proc.status_code == 200:
                                        st.session_state.consulta_atual = response_proc.json()
                                    else:
                                        st.error(f"Erro ao processar: {response_proc.text}")
                                else:
                                    st.warning("Nenhuma fala detetada no áudio.")
                            else:
                                st.error(f"Erro na transcrição: {response_transcricao.text}")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Erro de conexão: {e}")
                    st.rerun()

            st.markdown("---")
            st.markdown("##### Prontuário")
            st.text_area("Notas e Decisão Clínica:", height=150, key="prontuario_texto", placeholder="Insira aqui a sua decisão final, prescrição e notas...")

        with col2:
            st.markdown("##### Sugestão da IA")
            sugestao = st.session_state.consulta_atual.get('sugestao_ia', {})
            if sugestao:
                hipoteses = sugestao.get("hipoteses_diagnosticas", []); conduta = sugestao.get("sugestao_conduta", "N/A"); exames = sugestao.get("exames_sugeridos", []); confianca = sugestao.get("nivel_confianca_ia", 0.0)
                st.markdown("**Hipóteses:**"); 
                if hipoteses:
                    for h in hipoteses: st.markdown(f"- {h}")
                st.markdown("**Conduta Sugerida:**"); st.write(conduta)
                st.markdown("**Exames Sugeridos:**")
                if exames:
                    for e in exames: st.markdown(f"- {e}")
                st.markdown("---"); desenhar_indicador_confianca(confianca)
            else:
                st.info("Aguardando a escuta da consulta...")
        
        st.markdown("---")
        if st.button("⏹️ Finalizar Consulta", use_container_width=True, type="primary"):
            decisao_final = st.session_state.get("prontuario_texto", "Nenhuma nota inserida.")
            if not decisao_final.strip():
                st.warning("Por favor, insira a sua decisão final no campo de prontuário antes de finalizar.")
            else:
                st.session_state.etapa = 3
                st.rerun()

    def pagina_finalizacao():
        desenhar_jornada(3)
        decisao_final = st.session_state.get("prontuario_texto", "Nenhuma nota inserida.")
        st.info("A consulta será finalizada com a seguinte decisão clínica:")
        st.markdown(f"> _{decisao_final}_")
        
        if st.button("Confirmar e Salvar", use_container_width=True):
            with st.spinner("A finalizar e a gerar reflexão..."):
                dados = {"consulta_atual": st.session_state.consulta_atual, "decisao": {"decisao": decisao_final, "resumo": decisao_final}}
                try:
                    response = requests.post(f"{API_URL}/consulta/finalizar/{uid}", json=dados)
                    if response.status_code == 200:
                        st.session_state.ultima_reflexao = response.json().get("reflexao")
                    st.session_state.etapa = 1
                    st.session_state.consulta_atual = None
                    st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão ao finalizar: {e}")

    # ... (O resto do ficheiro, com a sidebar e o router principal, continua igual) ...
    with st.sidebar:
        st.title("🩺 ShaulaMed")
        email_utilizador = st.session_state.utilizador_logado.get('email', 'N/A')
        st.caption(f"Médico: {email_utilizador}")
        
        page_type = "primary" if st.session_state.pagina == "Consulta" else "secondary"
        if st.button("Consulta", use_container_width=True, type=page_type):
            st.session_state.pagina = "Consulta"
            st.rerun()

        page_type = "primary" if st.session_state.pagina == "Relatorio" else "secondary"
        if st.button("Painel Semanal", use_container_width=True, type=page_type):
            st.session_state.pagina = "Relatorio"
            if 'relatorio_semanal_completo' in st.session_state:
                del st.session_state.relatorio_semanal_completo
            st.rerun()
            
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.utilizador_logado = None
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if st.session_state.pagina == "Consulta":
        st.title("ShaulaMed Copilot")
        if st.session_state.etapa == 1: pagina_inicial()
        elif st.session_state.etapa == 2: pagina_consulta()
        elif st.session_state.etapa == 3: pagina_finalizacao()
    elif st.session_state.pagina == "Relatorio":
        # ... (código da pagina_relatorio)
        st.title("Painel Semanal")
        st.caption("Uma análise reflexiva da sua prática na última semana, gerada pela Shaula.")
        if st.button("Gerar Relatório da Semana", use_container_width=True):
            with st.spinner("A analisar as consultas da última semana..."):
                try:
                    response = requests.get(f"{API_URL}/medico/{uid}/relatorio_semanal", timeout=120)
                    if response.status_code == 200:
                        st.session_state.relatorio_semanal_completo = response.json()
                    else:
                        st.error(f"Erro ao gerar o relatório ({response.status_code}): {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}")
        if 'relatorio_semanal_completo' in st.session_state and st.session_state.relatorio_semanal_completo:
            relatorio_data = st.session_state.relatorio_semanal_completo
            texto_coach = relatorio_data.get("texto_coach")
            if texto_coach:
                texto_formatado_html = texto_coach.replace("\n", "<br>")
                st.markdown(f'<div class="report-box">{texto_formatado_html}</div>', unsafe_allow_html=True)
            dados_estruturados = relatorio_data.get("dados_estruturados")
            if dados_estruturados:
                st.markdown("---")
                st.subheader("Estatísticas da Semana")
                stats = dados_estruturados.get("stats_semanais", {})
                if stats:
                    stats_df = pd.DataFrame(list(stats.items()), columns=['Métrica', 'Valor'])
                    st.bar_chart(stats_df.set_index('Métrica'))
                st.markdown("---")
                st.subheader("Detalhe das Consultas")
                tabela_df = pd.DataFrame(dados_estruturados.get("tabela_concordancia", []))
                if not tabela_df.empty:
                    st.dataframe(tabela_df.set_index("Caso"), use_container_width=True)


if st.session_state.utilizador_logado:
    shaulamed_app()
else:
    pagina_login()