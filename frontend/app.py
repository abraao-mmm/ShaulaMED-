# app.py (Versão limpa e modular)

import streamlit as st
import requests
import pandas as pd
import random
from login import pagina_login
from bento_layout import render_bento_layout # <--- NOVA IMPORTAÇÃO

# --- CONFIGURAÇÃO DA PÁGINA E URL DA API ---
st.set_page_config(page_title="ShaulaMed", layout="centered", initial_sidebar_state="expanded")
API_URL = "https://shaulamed-api-1x9x.onrender.com"

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# (Esta seção permanece exatamente a mesma)
if 'utilizador_logado' not in st.session_state: st.session_state.utilizador_logado = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Consulta"
if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'consulta_atual' not in st.session_state: st.session_state.consulta_atual = None
if 'resultado_final' not in st.session_state: st.session_state.resultado_final = None
if 'decisao_a_finalizar' not in st.session_state: st.session_state.decisao_a_finalizar = None
if "audio_processado" not in st.session_state: st.session_state.audio_processado = False
if 'ultimo_documento' not in st.session_state: st.session_state.ultimo_documento = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL ---
def shaulamed_app():
    uid = st.session_state.utilizador_logado.get('localId')
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None
        st.rerun()
        return

    # Estilo CSS Global (pode manter o seu CSS base aqui)
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #0A0A2A; }
        [data-testid="stSidebar"] { background-color: #1E1E3F; }
        .stButton > button { border-radius: 8px; border: 1px solid #8A2BE2; background-color: transparent; color: #E0E0E0; }
        .stButton > button:hover { border-color: #E0E0E0; background-color: #6A1B9A; color: white; }
        .stButton > button[kind="primary"] { background-color: #8A2BE2; color: white; }
    </style>
    """, unsafe_allow_html=True)
    
    def pagina_inicial():
        # (Esta função permanece a mesma)
        if 'resultado_final' in st.session_state and st.session_state.resultado_final:
            resumo = st.session_state.resultado_final.get("texto_gerado_prontuario", "Nenhum resumo foi gerado.")
            st.subheader("Resumo da Última Consulta"); st.text_area("Texto para Prontuário:", value=resumo, height=250, key="resumo_final_display"); st.success("Resumo gerado com sucesso!")
            del st.session_state.resultado_final
        else:
            st.info(f"**Shaula:** \"_{random.choice(['Olá. Senti a sua presença. Em que parte da jornada estamos hoje?', 'Bem-vindo(a) de volta. O universo aguardava o seu raciocínio.'])}_\"")
        
        if st.button("▶️ Iniciar Nova Consulta", use_container_width=True, key="iniciar_consulta_btn"):
            #... (lógica para iniciar consulta)
            with st.spinner("A iniciar sessão de consulta..."):
                response = requests.post(f"{API_URL}/consulta/iniciar/{uid}", timeout=40)
                if response.status_code == 200:
                    st.session_state.consulta_atual = response.json(); st.session_state.etapa = 2; st.session_state.audio_processado = False; st.rerun()
                else:
                    st.error(f"Erro do servidor ({response.status_code}): {response.text}")
    
    # --- PÁGINA DE CONSULTA SIMPLIFICADA ---
    def pagina_consulta():
        render_bento_layout(uid, API_URL) # <--- ÚNICA LINHA NECESSÁRIA!

    def pagina_finalizacao():
        # (Esta função permanece a mesma)
        decisao_final = st.session_state.get("decisao_a_finalizar", "Nenhuma nota inserida.")
        st.info("A consulta será finalizada com a seguinte decisão clínica:"); st.markdown(f"> _{decisao_final}_")
        formato_selecionado = st.selectbox("Escolha o formato do resumo:", ("SOAP", "Livre (texto corrido)", "PEACE", "CAMPOS"))
        if st.button(f"Confirmar e Gerar Resumo {formato_selecionado}", use_container_width=True, key="confirmar_resumo_btn"):
            #... (lógica para finalizar consulta)
            with st.spinner(f"A finalizar e gerar o resumo..."):
                dados = {"consulta_atual": st.session_state.consulta_atual, "decisao": {"decisao": decisao_final, "resumo": decisao_final}, "formato_resumo": formato_selecionado}
                response = requests.post(f"{API_URL}/consulta/finalizar/{uid}", json=dados, timeout=120)
                if response.status_code == 200:
                    st.session_state.resultado_final = response.json(); st.session_state.etapa = 1; st.session_state.consulta_atual = None
                    if "decisao_a_finalizar" in st.session_state: del st.session_state.decisao_a_finalizar
                    st.rerun()
                else:
                    st.error(f"Erro ao finalizar ({response.status_code}): {response.text}")

    # (A barra lateral e o roteador de páginas permanecem os mesmos)
    with st.sidebar:
        st.title("🩺 ShaulaMed"); st.caption(f"Médico: {st.session_state.utilizador_logado.get('email', 'N/A')}")
        if st.button("Consulta", use_container_width=True, type=("primary" if st.session_state.pagina == "Consulta" else "secondary"), key="sidebar_consulta"):
            st.session_state.pagina = "Consulta"; st.rerun()
        if st.button("Painel Semanal", use_container_width=True, type=("primary" if st.session_state.pagina == "Relatorio" else "secondary"), key="sidebar_relatorio"):
            st.session_state.pagina = "Relatorio"
            if 'relatorio_semanal_completo' in st.session_state: del st.session_state.relatorio_semanal_completo
            st.rerun()
        st.markdown("---")
        if st.button("Sair", use_container_width=True, key="sidebar_sair"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    if st.session_state.pagina == "Consulta":
        st.title("ShaulaMed Copilot")
        if st.session_state.etapa == 1: pagina_inicial()
        elif st.session_state.etapa == 2: pagina_consulta()
        elif st.session_state.etapa == 3: pagina_finalizacao()
    elif st.session_state.pagina == "Relatorio":
        # (Página de relatório permanece a mesma)
        st.title("Painel Semanal")
        #...

# Roteador Principal (permanece o mesmo)
if 'utilizador_logado' in st.session_state and st.session_state.utilizador_logado:
    shaulamed_app()
else:
    pagina_login()