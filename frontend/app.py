# app.py (Versão Completa com Geração de Documentos)

import streamlit as st
import requests
import pandas as pd
import random
from login import pagina_login
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAÇÃO DA PÁGINA E URL DA API ---
st.set_page_config(
    page_title="ShaulaMed",
    layout="centered",
    initial_sidebar_state="expanded"
)
# Certifique-se de que a URL está correta para o seu ambiente de produção
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
if 'resultado_final' not in st.session_state:
    st.session_state.resultado_final = None
if 'decisao_a_finalizar' not in st.session_state:
    st.session_state.decisao_a_finalizar = None
if "audio_processado" not in st.session_state:
    st.session_state.audio_processado = False
if 'ultimo_documento' not in st.session_state:
    st.session_state.ultimo_documento = None

# --- FUNÇÃO DA APLICAÇÃO PRINCIPAL ---
def shaulamed_app():
    uid = st.session_state.utilizador_logado.get('localId')
    if not uid:
        st.error("Erro de sessão. Por favor, faça o login novamente.")
        st.session_state.utilizador_logado = None
        st.rerun()
        return

    # Estilo CSS
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #0A0A2A; }
        [data-testid="stSidebar"] { background-color: #1E1E3F; }
        .stButton > button { border-radius: 8px; border: 1px solid #8A2BE2; background-color: transparent; color: #E0E0E0; transition: all 0.2s ease-in-out; }
        .stButton > button:hover { border-color: #E0E0E0; background-color: #6A1B9A; color: white; }
        .stButton > button[kind="primary"] { background-color: #8A2BE2; color: white; }
        .st-emotion-cache-16txtl3 { padding-top: 2rem; }
        .step-active { font-weight: bold; color: #E0E0E0; border-bottom: 2px solid #8A2BE2; padding-bottom: 5px; }
        .step-inactive { color: #555; }
        .report-box { background-color: #1E1E3F; border-left: 5px solid #8A2BE2; padding: 20px; border-radius: 8px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    FRASES_BOAS_VINDAS = ["Olá. Senti a sua presença. Em que parte da jornada estamos hoje?", "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio."]

    def desenhar_jornada(etapa_atual=1):
        etapas = ["1. Iniciar", "2. Processar", "3. Finalizar"]
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f'<p class="{"step-active" if (i+1) == etapa_atual else "step-inactive"}">{etapas[i]}</p>', unsafe_allow_html=True)
        st.markdown("---")

    def pagina_inicial():
        if 'resultado_final' in st.session_state and st.session_state.resultado_final:
            resumo = st.session_state.resultado_final.get("texto_gerado_prontuario", "Nenhum resumo foi gerado.")
            reflexao = st.session_state.resultado_final.get("reflexao", "")
            
            st.subheader("Resumo da Última Consulta")
            st.text_area("Texto para Prontuário:", value=resumo, height=250, key="resumo_final_display")
            st.success("Resumo gerado com sucesso!")
            if reflexao:
                st.info(f"**Reflexão da Shaula:** \"_{reflexao}_\"")
            st.markdown("---")
            
            del st.session_state.resultado_final
        else:
             st.info(f"**Shaula:** \"_{random.choice(FRASES_BOAS_VINDAS)}_\"")

        desenhar_jornada(1)
        if st.button("▶️ Iniciar Nova Consulta", use_container_width=True, key="iniciar_consulta_btn"):
            with st.spinner("A iniciar sessão de consulta..."):
                try:
                    response = requests.post(f"{API_URL}/consulta/iniciar/{uid}", timeout=40)
                    if response.status_code == 200:
                        st.session_state.consulta_atual = response.json()
                        st.session_state.etapa = 2
                        st.session_state.audio_processado = False
                        st.rerun()
                    else:
                        st.error(f"O servidor da API respondeu com um erro ({response.status_code}). Detalhe: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}.")

    def pagina_consulta():
        desenhar_jornada(2)
        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.markdown("##### Captura da Consulta")
            audio_info = mic_recorder(
                start_prompt="▶️ Iniciar Escuta",
                stop_prompt="⏹️ Parar e Analisar",
                key='recorder'
            )

            if audio_info and audio_info['bytes'] and not st.session_state.audio_processado:
                st.session_state.audio_processado = True
                audio_bytes = audio_info['bytes']
                with st.spinner("A transcrever, estruturar e analisar a consulta..."):
                    try:
                        files = {'ficheiro_audio': ("audio.wav", audio_bytes, "audio/wav")}
                        response_transcricao = requests.post(f"{API_URL}/audio/transcrever", files=files, timeout=90)

                        if response_transcricao.status_code == 200:
                            texto_transcrito = response_transcricao.json().get("texto_transcrito", "")
                            if texto_transcrito:
                                dados_proc = {"consulta_atual": st.session_state.consulta_atual, "fala": {"texto": texto_transcrito}}
                                response_proc = requests.post(f"{API_URL}/consulta/processar/{uid}", json=dados_proc, timeout=180)
                                
                                if response_proc.status_code == 200:
                                    st.session_state.consulta_atual = response_proc.json()
                                    st.session_state.ultimo_documento = None
                                    st.rerun()
                                else:
                                    st.error(f"Erro ao processar a consulta: {response_proc.text}")
                                    st.session_state.audio_processado = False
                            else:
                                st.warning("Nenhuma fala detetada no áudio.")
                                st.session_state.audio_processado = False
                        else:
                            st.error(f"Erro na transcrição: {response_transcricao.text}")
                            st.session_state.audio_processado = False
                    except requests.exceptions.RequestException as e:
                        st.error(f"Erro de conexão com a API: {e}")
                        st.session_state.audio_processado = False

            st.markdown("---")
            st.markdown("##### Prontuário")
            st.text_area("Sua Decisão Clínica e Notas Adicionais:", height=150, key="prontuario_texto", placeholder="Insira aqui a sua conduta final, prescrição e notas para o prontuário...")

        with col2:
            st.markdown("##### Análise Estruturada da Shaula")
            sugestao_ia = st.session_state.consulta_atual.get('sugestao_ia', {})
            nota_clinica = sugestao_ia.get('nota_clinica_estruturada', {})
            analise_avancada = sugestao_ia.get('analise_clinica_avancada', {})

            if nota_clinica and not nota_clinica.get("erro"):
                titulos = {
                    "queixa_principal": "Queixa Principal", "historia_doenca_atual": "História da Doença Atual (HDA)",
                    "antecedentes_pessoais_familiares": "Antecedentes", "medicamentos_em_uso": "Medicamentos em Uso",
                    "exame_fisico_verbalizado": "Exame Físico", "hipoteses_diagnosticas": "Hipóteses Diagnósticas",
                    "conduta_sugerida": "Conduta Sugerida pela IA", "orientacoes_gerais": "Orientações",
                    "retorno_encaminhamento": "Retorno / Encaminhamentos"
                }
                for chave, titulo in titulos.items():
                    conteudo = nota_clinica.get(chave)
                    if conteudo:
                        st.markdown(f"**{titulo}**"); st.write(conteudo if not isinstance(conteudo, list) else "\n".join(f"- {item}" for item in conteudo)); st.markdown("---")
            
            elif not sugestao_ia:
                 st.info("Aguardando a escuta da consulta para gerar a nota clínica...")
            
            if analise_avancada and not analise_avancada.get("erro"):
                st.markdown("##### 🔬 Insights e Alertas da IA")
                if analise_avancada.get("exames_complementares_sugeridos"):
                    with st.expander("Sugestões de Exames Complementares"):
                        for item in analise_avancada["exames_complementares_sugeridos"]: st.markdown(f"- **{item['exame']}:** _{item['justificativa']}_")
                if analise_avancada.get("alertas_de_conduta"):
                    with st.expander("⚠️ Alertas de Conduta"):
                        for item in analise_avancada["alertas_de_conduta"]: st.warning(f"**{item['alerta']}:** {item['explicacao_risco']}")
                if analise_avancada.get("sugestoes_de_tratamento"):
                    with st.expander("💊 Sugestões de Tratamento"):
                        for item in analise_avancada["sugestoes_de_tratamento"]: st.markdown(f"**{item['medicamento_sugerido']} ({item['posologia_recomendada']})**"); st.caption(f"Justificativa: {item['justificativa_clinica']}")
                if analise_avancada.get("validacao_medicamentos_mencionados"):
                    with st.expander("✅ Validação de Medicamentos"):
                         for item in analise_avancada["validacao_medicamentos_mencionados"]: st.info(f"**{item['medicamento_mencionado']}:** {item['status_validacao']} - _{item['observacao']}_")

            # Seção para Geração de Documentos
            st.markdown("##### 📄 Gerar Documentos")
            tipos_documentos = {"Receita": "receita", "Pedido de Exame": "pedido_exame", "Atestado": "atestado", "Encaminhamento": "encaminhamento", "Relatório": "relatorio_convenio"}
            cols_docs = st.columns(len(tipos_documentos))
            for i, (nome_botao, tipo_doc) in enumerate(tipos_documentos.items()):
                if cols_docs[i].button(nome_botao, key=f"btn_{tipo_doc}", use_container_width=True):
                    with st.spinner(f"A gerar {nome_botao}..."):
                        try:
                            payload = {"tipo_documento": tipo_doc, "dados_consulta": st.session_state.consulta_atual.get('sugestao_ia', {})}
                            response = requests.post(f"{API_URL}/consulta/gerar_documento/{uid}", json=payload, timeout=60)
                            if response.status_code == 200:
                                st.session_state.ultimo_documento = response.json().get("documento_gerado")
                            else:
                                st.error(f"Erro ao gerar documento: {response.text}")
                        except Exception as e:
                            st.error(f"Erro de conexão ao gerar documento: {e}")
            
            if st.session_state.get('ultimo_documento'):
                with st.expander("Visualizar Último Documento Gerado", expanded=True):
                    st.text_area("Texto do Documento:", value=st.session_state.ultimo_documento, height=300, key="doc_gerado_display")

        st.markdown("---")
        if st.button("⏹️ Finalizar Consulta", use_container_width=True, type="primary", key="finalizar_consulta_btn"):
            decisao_final = st.session_state.get("prontuario_texto", "")
            if not decisao_final.strip():
                st.warning("Por favor, insira a sua decisão clínica final no campo de prontuário antes de finalizar.")
            else:
                st.session_state.decisao_a_finalizar = decisao_final
                st.session_state.etapa = 3
                st.rerun()

    def pagina_finalizacao():
        desenhar_jornada(3)
        decisao_final = st.session_state.get("decisao_a_finalizar", "Nenhuma nota inserida.")
        st.info("A consulta será finalizada com a seguinte decisão clínica:"); st.markdown(f"> _{decisao_final}_")
        st.markdown("---")
        st.markdown("##### Gerar Resumo para Prontuário")
        formato_selecionado = st.selectbox("Escolha o formato do resumo:", ("SOAP", "Livre (texto corrido)", "PEACE", "CAMPOS"))
        if st.button(f"Confirmar e Gerar Resumo {formato_selecionado}", use_container_width=True, key="confirmar_resumo_btn"):
            with st.spinner(f"A finalizar e gerar o resumo no formato {formato_selecionado}..."):
                dados = {"consulta_atual": st.session_state.consulta_atual, "decisao": {"decisao": decisao_final, "resumo": decisao_final}, "formato_resumo": formato_selecionado}
                try:
                    response = requests.post(f"{API_URL}/consulta/finalizar/{uid}", json=dados, timeout=120)
                    if response.status_code == 200:
                        st.session_state.resultado_final = response.json()
                        st.session_state.etapa = 1
                        st.session_state.consulta_atual = None
                        if "decisao_a_finalizar" in st.session_state: del st.session_state.decisao_a_finalizar
                        st.rerun()
                    else:
                        st.error(f"Erro ao finalizar ({response.status_code}): {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão ao finalizar: {e}")

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
        st.title("Painel Semanal")
        st.caption("Uma análise reflexiva da sua prática na última semana, gerada pela Shaula.")
        if st.button("Gerar Relatório da Semana", use_container_width=True, key="gerar_relatorio_btn"):
            with st.spinner("A analisar as consultas da última semana..."):
                try:
                    response = requests.get(f"{API_URL}/medico/{uid}/relatorio_semanal", timeout=120)
                    if response.status_code == 200: st.session_state.relatorio_semanal_completo = response.json()
                    else: st.error(f"Erro ao gerar o relatório ({response.status_code}): {response.text}")
                except requests.exceptions.RequestException as e: st.error(f"Erro de conexão: {e}")
        if 'relatorio_semanal_completo' in st.session_state and st.session_state.relatorio_semanal_completo:
            relatorio_data = st.session_state.relatorio_semanal_completo
            if relatorio_data.get("texto_coach"): st.markdown(f'<div class="report-box">{relatorio_data.get("texto_coach").replace("n", "<br>")}</div>', unsafe_allow_html=True)
            if relatorio_data.get("dados_estruturados"):
                st.markdown("---"); st.subheader("Estatísticas da Semana")
                if relatorio_data["dados_estruturados"].get("stats_semanais"): st.bar_chart(pd.DataFrame(list(relatorio_data["dados_estruturados"]["stats_semanais"].items()), columns=['Métrica', 'Valor']).set_index('Métrica'))
                st.markdown("---"); st.subheader("Detalhe das Consultas")
                if not pd.DataFrame(relatorio_data["dados_estruturados"].get("tabela_concordancia", [])).empty: st.dataframe(pd.DataFrame(relatorio_data["dados_estruturados"]["tabela_concordancia"]).set_index("Caso"), use_container_width=True)

if 'utilizador_logado' in st.session_state and st.session_state.utilizador_logado:
    shaulamed_app()
else:
    pagina_login()