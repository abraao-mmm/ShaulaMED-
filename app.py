# app.py

import streamlit as st
import requests
import json
import random
from streamlit_mic_recorder import mic_recorder
from login import pagina_login

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL (O CORAÇÃO DO SHAULAMED) ---
def shaulamed_app():
    API_URL = "https://shaulamed-api.onrender.com" # A sua URL do Render
    uid = st.session_state.utilizador_logado.get('localId') if st.session_state.utilizador_logado else None
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None; st.rerun()
        return

    # Configuração da Página e Estilo
    st.set_page_config(page_title="ShaulaMed Copilot", layout="centered", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
        /* ... (O seu CSS customizado aqui) ... */
    </style>
    """, unsafe_allow_html=True)

    # Inicialização do estado da sessão da aplicação
    if 'pagina' not in st.session_state: st.session_state.pagina = "Consulta"
    if 'etapa' not in st.session_state: st.session_state.etapa = 1
    if 'sugestao' not in st.session_state: st.session_state.sugestao = None
    if 'texto_transcrito' not in st.session_state: st.session_state.texto_transcrito = ""

    # ... (As suas funções auxiliares desenhar_jornada e desenhar_indicador_confianca aqui) ...

    def pagina_consulta():
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("##### Gravação da Consulta")
            audio_gravado = mic_recorder(start_prompt="🎙️ Gravar Fala", stop_prompt="⏹️ Parar", key='recorder', format="wav")
            if audio_gravado:
                st.session_state.audio_gravado = audio_gravado['bytes']; st.audio(audio_gravado['bytes'])
            if 'audio_gravado' in st.session_state and st.session_state.audio_gravado:
                if st.button("Processar Áudio"):
                    with st.spinner("A enviar áudio e a processar..."):
                        ficheiros = {'ficheiro_audio': ('audio.wav', st.session_state.audio_gravado, 'audio/wav')}
                        response_transcricao = requests.post(f"{API_URL}/audio/transcrever", files=ficheiros)
                        if response_transcricao.status_code == 200:
                            texto = response_transcricao.json().get("texto_transcrito")
                            st.session_state.texto_transcrito = texto
                            response_processamento = requests.post(f"{API_URL}/consulta/processar/{uid}", json={"texto": texto})
                            if response_processamento.status_code == 200: st.session_state.sugestao = response_processamento.json().get("sugestao")
                            else: st.error("Erro ao processar a fala na API.")
                        else: st.error(f"Erro na transcrição: {response_transcricao.text}")
                        st.session_state.audio_gravado = None; st.rerun()
        # ... (O resto do código da pagina_consulta aqui) ...

    # ... (O resto das suas funções de página aqui: pagina_inicial, pagina_finalizacao, etc.) ...
    
    # --- Lógica de Navegação da Aplicação Principal ---
    with st.sidebar:
        # ... (O seu código da barra lateral aqui) ...
        pass
    st.title("ShaulaMed Copilot")
    # ... (O seu código do router de páginas aqui) ...

# --- ROUTER PRINCIPAL (O "PORTEIRO") ---
if st.session_state.utilizador_logado:
    shaulamed_app()
else:
    st.set_page_config(page_title="Login - ShaulaMed")
    pagina_login()