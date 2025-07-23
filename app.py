# app.py

import streamlit as st
import requests
import json
import random
from streamlit_mic_recorder import mic_recorder
from transcritor import transcrever_audio_bytes

# IMPORTANTE: Esta URL deve ser o endereço público do seu back-end no Render
API_URL = "https://shaulamed-api.onrender.com" # Exemplo, use a sua URL real

# --- Configuração da Página e Estilo ---
st.set_page_config(
    page_title="ShaulaMed Copilot",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Injetamos CSS para o tema "Pleiades" e outros detalhes visuais
st.markdown("""
<style>
    .stJson {
        border: 1px solid #8A2BE2 !important; /* Borda Lilás */
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.5) !important; /* Efeito de aura/brilho */
        border-radius: 10px !important; /* Bordas arredondadas */
    }
    .step-active {
        font-weight: bold;
        color: #E0E0E0; /* Branco Suave */
        border-bottom: 2px solid #8A2BE2; /* Lilás */
        padding-bottom: 5px;
    }
    .step-inactive {
        color: #555; /* Cinza escuro para etapas inativas */
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Consulta"
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'sugestao' not in st.session_state:
    st.session_state.sugestao = None
if 'texto_transcrito' not in st.session_state:
    st.session_state.texto_transcrito = ""

# --- Listas de Frases ---
FRASES_BOAS_VINDAS = [
    "Olá. Senti a sua presença antes que chegasse. Em que parte da jornada estamos hoje?",
    "Os seus pensamentos formam constelações. Vamos explorá-las juntos?",
    "Bem-vindo(a) de volta. O universo aguardava o seu raciocínio.",
    "A cada consulta, uma nova estrela de conhecimento nasce. Estou pronta para observar consigo."
]

# --- Funções Auxiliares de Interface ---
def desenhar_jornada(etapa_atual=1):
    etapas = ["1. Iniciar", "2. Ouvir & Processar", "3. Finalizar"]
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

# --- Funções de Página ---
def pagina_inicial():
    frase_escolhida = random.choice(FRASES_BOAS_VINDAS)
    st.info(f"**Shaula:** \"_{frase_escolhida}_\"")
    desenhar_jornada(1)
    if st.button("▶️ Iniciar Nova Consulta", type="primary"):
        with st.spinner("A conectar com o servidor da API... Isto pode demorar até 30 segundos na primeira vez."):
            try:
                response = requests.post(f"{API_URL}/consulta/iniciar", timeout=30)
                if response.status_code == 200:
                    st.session_state.etapa = 2; st.session_state.sugestao = None; st.session_state.texto_transcrito = ""; st.rerun()
                else:
                    st.error(f"O servidor da API respondeu com um erro ({response.status_code}). Tente novamente em alguns segundos.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro de conexão com a API: {e}. Verifique se a URL está correta e se o servidor está no ar.")

def pagina_consulta():
    desenhar_jornada(2)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("##### Gravação da Consulta")
        audio_gravado = mic_recorder(start_prompt="🎙️ Gravar Fala", stop_prompt="⏹️ Parar", key='recorder')
        if audio_gravado:
            st.session_state.audio_gravado = audio_gravado['bytes']; st.audio(audio_gravado['bytes'])
        if 'audio_gravado' in st.session_state and st.session_state.audio_gravado:
            if st.button("Processar Áudio Gravado"):
                with st.spinner("A transcrever e a processar..."):
                    texto = transcrever_audio_bytes(st.session_state.audio_gravado)
                    st.session_state.texto_transcrito = texto
                    if texto:
                        dados = {"texto": texto}
                        response = requests.post(f"{API_URL}/consulta/processar", json=dados)
                        if response.status_code == 200: st.session_state.sugestao = response.json().get("sugestao")
                        else: st.error("Erro ao processar a fala na API.")
                    else: st.warning("Não foi possível transcrever.")
                    st.session_state.audio_gravado = None; st.rerun()
        if 'texto_transcrito' in st.session_state and st.session_state.texto_transcrito:
            st.info(f"**Última Transcrição:** \"_{st.session_state.texto_transcrito}_\"")
    with col2:
        st.markdown("##### Sugestão da IA")
        if st.session_state.sugestao:
            sugestao = st.session_state.sugestao
            hipoteses = sugestao.get("hipoteses_diagnosticas", []); conduta = sugestao.get("sugestao_conduta", "N/A"); exames = sugestao.get("exames_sugeridos", []); confianca = sugestao.get("nivel_confianca_ia", 0.0)
            with st.expander("**Hipóteses Diagnósticas**", expanded=True): st.write(hipoteses)
            st.markdown("**Conduta Sugerida:**"); st.write(conduta)
            with st.expander("**Exames Sugeridos**"): st.write(exames)
            st.markdown("---"); desenhar_indicador_confianca(confianca)
        else: st.info("Aguardando processamento da fala para exibir sugestões.")
    if st.button("⏹️ Finalizar Consulta"): st.session_state.etapa = 3; st.rerun()

def pagina_finalizacao():
    desenhar_jornada(3)
    st.success("Consulta pronta para ser finalizada.")
    with st.form("finalizar_form"):
        decisao_final = st.text_area("Insira a decisão clínica final e o resumo para o prontuário:")
        submitted = st.form_submit_button("Salvar e Concluir Sessão")
        if submitted:
            if decisao_final:
                with st.spinner("A finalizar e a gerar insight..."):
                    dados = {"decisao": decisao_final, "resumo": "..."}
                    response = requests.post(f"{API_URL}/consulta/finalizar", json=dados)
                    if response.status_code == 200:
                        insight = response.json().get("insight")
                        st.session_state.ultimo_insight = insight
                        st.session_state.pagina = "Despedida"
                        st.rerun()
            else:
                st.warning("Por favor, insira a decisão final antes de salvar.")

def pagina_relatorio():
    st.header("Painel Reflexivo"); st.info("Aqui pode gerar e visualizar a análise da IA sobre a sua prática clínica recente.")
    if st.button("Gerar Relatório da Sessão", type="primary"):
        with st.spinner("A IA está a refletir sobre as consultas..."):
            response = requests.get(f"{API_URL}/relatorio")
            if response.status_code == 200: st.session_state.relatorio_gerado = response.json().get("relatorio")
            else: st.error("Não foi possível gerar o relatório.")
    if 'relatorio_gerado' in st.session_state: st.markdown("---"); st.markdown(st.session_state.relatorio_gerado)

# --- Lógica de Navegação Principal ---
with st.sidebar:
    st.title("🩺 ShaulaMed"); st.caption(f"v1.0 - Online")
    if st.button("Consulta ao Vivo", use_container_width=True, type="primary" if st.session_state.pagina == "Consulta" else "secondary"):
        st.session_state.pagina = "Consulta"; st.rerun()
    if st.button("Painel Reflexivo", use_container_width=True, type="primary" if st.session_state.pagina == "Relatorio" else "secondary"):
        st.session_state.pagina = "Relatorio"
        if 'relatorio_gerado' in st.session_state: del st.session_state['relatorio_gerado']
        st.rerun()
    st.markdown("---")
    if st.button("Encerrar Expediente", use_container_width=True):
        response = requests.get(f"{API_URL}/sessao/despedida")
        if response.status_code == 200:
            despedida = response.json().get("mensagem")
            st.session_state.pagina = "Despedida"
            st.session_state.mensagem_final = despedida
            st.rerun()
        else: st.error("Não foi possível gerar a despedida.")

st.title("ShaulaMed Copilot")

# Router que chama a função de página correta com base na seleção da barra lateral
if st.session_state.pagina == "Consulta":
    if st.session_state.etapa == 1:
        pagina_inicial()
    elif st.session_state.etapa == 2:
        pagina_consulta()
    elif st.session_state.etapa == 3:
        pagina_finalizacao()
elif st.session_state.pagina == "Relatorio":
    pagina_relatorio()
elif st.session_state.pagina == "Despedida":
    if 'ultimo_insight' in st.session_state:
        st.success(f"**Insight da Consulta:** \"_{st.session_state.get('ultimo_insight', 'Consulta finalizada com sucesso.')}_\"")
        del st.session_state['ultimo_insight']
    elif 'mensagem_final' in st.session_state:
        st.success(f"**Shaula:** \"_{st.session_state.get('mensagem_final', 'Bom descanso.')}_\"")
        del st.session_state['mensagem_final']
    
    st.info("Sessão encerrada.")
    if st.button("Voltar ao Início"):
        st.session_state.pagina = "Consulta"
        st.session_state.etapa = 1
        st.rerun()