# app.py (Versão de Teste com Entrada de Texto)

import streamlit as st
import requests
import json
import random
# from streamlit_mic_recorder import mic_recorder  # <<< REMOVIDO
# from transcritor import transcrever_audio_bytes # <<< REMOVIDO
from login import pagina_login

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'utilizador_logado' not in st.session_state:
    st.session_state.utilizador_logado = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL (SHAULAMED) ---
def shaulamed_app():
    API_URL = "https://shaulamed-api-1x9x.onrender.com" # A sua URL do Render
    uid = st.session_state.utilizador_logado.get('localId') if st.session_state.utilizador_logado else None
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None; st.rerun()
        return

    # (Configuração da Página, CSS, e Funções Auxiliares continuam os mesmos)
    st.set_page_config(page_title="ShaulaMed Copilot", layout="centered", initial_sidebar_state="expanded")
    st.markdown("""...""") # O seu CSS aqui

    # ... (O resto das suas funções, listas de frases, etc., aqui)

    def pagina_consulta():
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.markdown("##### Relato do Paciente (via Texto)")
            
            # --- LÓGICA DE INTERFACE SIMPLIFICADA ---
            # Substituímos o gravador por uma caixa de texto
            fala_paciente = st.text_area("Insira a fala do paciente aqui:", height=150, key="fala_texto")
            
            if st.button("Processar Relato"):
                if fala_paciente:
                    with st.spinner("A processar..."):
                        st.session_state.texto_transcrito = fala_paciente
                        # Enviamos o texto diretamente para o endpoint de processamento
                        dados = {"texto": fala_paciente}
                        response = requests.post(f"{API_URL}/consulta/processar/{uid}", json=dados)
                        
                        if response.status_code == 200:
                            st.session_state.sugestao = response.json().get("sugestao")
                        else:
                            st.error("Erro ao processar o texto na API.")
                        st.rerun()
                else:
                    st.warning("Por favor, insira o relato do paciente.")

            if st.session_state.texto_transcrito:
                st.info(f"**Último Relato Processado:** \"_{st.session_state.texto_transcrito}_\"")

        with col2:
            # (A lógica de exibição da sugestão continua a mesma)
            st.markdown("##### Sugestão da IA")
            if st.session_state.sugestao:
                # ... (código para exibir hipóteses, conduta, confiança, etc.)
                pass
            else:
                st.info("Aguardando processamento do relato para exibir sugestões.")
        
        if st.button("⏹️ Finalizar Consulta"):
            st.session_state.etapa = 3
            st.rerun()

    # (O resto do seu código, com as outras páginas, a barra lateral e o router, pode permanecer o mesmo)

# --- ROUTER PRINCIPAL (O "PORTEIRO") ---
if st.session_state.utilizador_logado:
    shaulamed_app()
else:
    # A configuração da página de login deve estar aqui para evitar erros
    st.set_page_config(page_title="Login - ShaulaMed")
    pagina_login()