# app.py

import streamlit as st
import requests
import json
from streamlit_mic_recorder import mic_recorder
from transcritor import transcrever_audio_bytes

# IMPORTANTE: Esta URL deve ser o endereço público do seu back-end no Render
API_URL = "https://shaulamed-api.onrender.com" # Exemplo, use a sua URL real

# --- Configuração da Página e Estilo ---
st.set_page_config(
    page_title="ShaulaMed Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injetamos CSS para o tema "Pleiades" e outros detalhes visuais
st.markdown("""
<style>
    .stJson {
        border: 1px solid #8A2BE2 !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.5) !important;
        border-radius: 10px !important;
    }
    .step-active { font-weight: bold; color: #E0E0E0; border-bottom: 2px solid #8A2BE2; padding-bottom: 5px; }
    .step-inactive { color: #555; }
</style>
""", unsafe_allow_html=True)

# --- Funções Auxiliares de Interface ---

def desenhar_jornada(etapa_atual=1):
    etapas = ["1. Iniciar", "2. Ouvir & Processar", "3. Finalizar"]
    cols = st.columns(3)
    for i, col in enumerate(cols):
        with col:
            if (i + 1) == etapa_atual:
                st.markdown(f'<p class="step-active">{etapas[i]}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="step-inactive">{etapas[i]}</p>', unsafe_allow_html=True)
    st.markdown("---")

def desenhar_indicador_confianca(nivel: float):
    if not isinstance(nivel, (float, int)):
        try:
            nivel = float(str(nivel).split(" ")[0].replace(",", "."))
        except (ValueError, IndexError):
            nivel = 0.0
    estrelas_preenchidas = int(nivel * 10)
    estrelas_vazias = 10 - estrelas_preenchidas
    display_html = f"<div style='font-size: 1.2rem; color: #FFD700;'>{'★' * estrelas_preenchidas}<span style='color: #555;'>{'☆' * estrelas_vazias}</span></div>"
    st.markdown("##### Nível de Confiança da IA")
    st.markdown(display_html, unsafe_allow_html=True)

# --- Funções de Página ---

def pagina_consulta():
    st.header("Consulta ao Vivo")
    
    if 'etapa' not in st.session_state: st.session_state.etapa = 1

    if st.session_state.etapa == 1:
        desenhar_jornada(1)
        st.info("Clique em 'Iniciar Nova Consulta' para começar a sessão.")
        if st.button("▶️ Iniciar Nova Consulta", type="primary"):
            response = requests.post(f"{API_URL}/consulta/iniciar")
            if response.status_code == 200:
                st.session_state.etapa = 2
                st.session_state.sugestao = None
                st.session_state.texto_transcrito = ""
                st.rerun()
            else:
                st.error(f"API offline ou com erro. Status: {response.status_code}")

    elif st.session_state.etapa == 2:
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("##### Gravação da Consulta")
            audio_gravado = mic_recorder(start_prompt="🎙️ Gravar Fala", stop_prompt="⏹️ Parar", key='recorder')
            
            if audio_gravado:
                st.session_state.audio_gravado = audio_gravado['bytes']
                st.audio(audio_gravado['bytes'])

            if 'audio_gravado' in st.session_state and st.session_state.audio_gravado:
                if st.button("Processar Áudio Gravado"):
                    with st.spinner("A transcrever e a processar..."):
                        texto = transcrever_audio_bytes(st.session_state.audio_gravado)
                        st.session_state.texto_transcrito = texto
                        if texto:
                            dados = {"texto": texto}
                            response = requests.post(f"{API_URL}/consulta/processar", json=dados)
                            if response.status_code == 200:
                                st.session_state.sugestao = response.json().get("sugestao")
                            else: st.error("Erro ao processar a fala na API.")
                        else: st.warning("Não foi possível transcrever.")
                        st.session_state.audio_gravado = None
                        st.rerun()

            if 'texto_transcrito' in st.session_state and st.session_state.texto_transcrito:
                st.info(f"**Última Transcrição:** \"_{st.session_state.texto_transcrito}_\"")

        with col2:
            st.markdown("##### Sugestão da IA")
            if st.session_state.sugestao:
                sugestao = st.session_state.sugestao
                hipoteses = sugestao.get("hipoteses_diagnosticas", [])
                conduta = sugestao.get("sugestao_conduta", "N/A")
                exames = sugestao.get("exames_sugeridos", [])
                confianca = sugestao.get("nivel_confianca_ia", 0.0)
                with st.expander("**Hipóteses Diagnósticas**", expanded=True): st.write(hipoteses)
                st.markdown("**Conduta Sugerida:**"); st.write(conduta)
                with st.expander("**Exames Sugeridos**"): st.write(exames)
                st.markdown("---"); desenhar_indicador_confianca(confianca)
            else:
                st.info("Aguardando processamento da fala para exibir sugestões.")
        
        if st.button("⏹️ Finalizar Consulta"):
            st.session_state.etapa = 3
            st.rerun()

    elif st.session_state.etapa == 3:
        desenhar_jornada(3)
        st.success("Consulta pronta para ser finalizada.")
        with st.form("finalizar_form"):
            decisao_final = st.text_area("Insira a decisão clínica final e o resumo para o prontuário:")
            submitted = st.form_submit_button("Salvar e Concluir Sessão")
            if submitted:
                if decisao_final:
                    dados = {"decisao": decisao_final, "resumo": "..."}
                    requests.post(f"{API_URL}/consulta/finalizar", json=dados)
                    st.session_state.etapa = 1
                    st.info("Consulta finalizada e salva com sucesso!")
                    st.balloons()
                else:
                    st.warning("Por favor, insira a decisão final antes de salvar.")

def pagina_relatorio():
    st.header("Painel Reflexivo")
    st.info("Aqui pode gerar e visualizar a análise da IA sobre a sua prática clínica recente.")
    if st.button("Gerar Relatório da Sessão", type="primary"):
        with st.spinner("A IA está a refletir sobre as consultas..."):
            response = requests.get(f"{API_URL}/relatorio")
            if response.status_code == 200:
                st.session_state.relatorio_gerado = response.json().get("relatorio")
            else:
                st.error("Não foi possível gerar o relatório.")
    if 'relatorio_gerado' in st.session_state:
        st.markdown("---"); st.markdown(st.session_state.relatorio_gerado)

# --- Lógica de Navegação Principal ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Consulta"

with st.sidebar:
    st.title("🩺 ShaulaMed")
    st.caption(f"v0.7 - Online")
    
    if st.button("Consulta ao Vivo", use_container_width=True, type="primary" if st.session_state.pagina == "Consulta" else "secondary"):
        st.session_state.pagina = "Consulta"
        st.rerun()
    if st.button("Painel Reflexivo", use_container_width=True, type="primary" if st.session_state.pagina == "Relatorio" else "secondary"):
        st.session_state.pagina = "Relatorio"
        if 'relatorio_gerado' in st.session_state: del st.session_state['relatorio_gerado']
        st.rerun()

if st.session_state.pagina == "Consulta":
    pagina_consulta()
elif st.session_state.pagina == "Relatorio":
    pagina_relatorio()