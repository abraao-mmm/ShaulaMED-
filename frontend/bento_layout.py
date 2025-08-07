# bento_layout.py

import streamlit as st
from style import get_css
from streamlit_mic_recorder import mic_recorder

def render_bento_layout(uid, API_URL):
    """
    Renderiza o layout completo do Bento Grid para a página de consulta.
    """
    # 1. Injeta o CSS na página
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # 2. Define os placeholders para o conteúdo de cada bloco
    # No futuro, substituiremos isso pelos dados reais da API
    insights_content = st.container()
    overview_content = st.container()
    efficiency_content = st.container()
    connectivity_content = st.container()
    protection_content = st.container()
    collaboration_content = st.container()

    # 3. Cria a estrutura HTML do grid usando colunas do Streamlit
    # Esta abordagem é mais robusta para conter widgets do Streamlit
    
    row1_col1, row1_col2, row1_col3 = st.columns([2, 2, 2])
    with row1_col1:
        with insights_content:
             st.markdown('<div class="bento-card insights"><h3>Insights</h3><div class="content"><p>Gravador e Transcrição</p></div></div>', unsafe_allow_html=True)

    with row1_col2:
        with overview_content:
            st.markdown('<div class="bento-card overview"><h3>Overview</h3><div class="content"><p>Queixa Principal</p></div></div>', unsafe_allow_html=True)

    with row1_col3:
        with collaboration_content:
            st.markdown('<div class="bento-card collaboration" style="grid-row: span 2; min-height: 320px;"><h3>Collaboration</h3><div class="content"><p>Documentos e Prontuário</p></div></div>', unsafe_allow_html=True)

    row2_col1, row2_col2 = st.columns([4, 2])
    with row2_col1:
        with efficiency_content:
            st.markdown('<div class="bento-card efficiency" style="grid-row: span 2; min-height: 320px;"><h3>Efficiency</h3><div class="content"><p>HDA, Antecedentes e Hipóteses</p></div></div>', unsafe_allow_html=True)

    row3_col1, row3_col2 = st.columns([4, 2])
    with row3_col1:
        # Este espaço está sob a célula 'efficiency', então pode ser usado para outros elementos se necessário
        pass
    with row3_col2:
         with connectivity_content:
            st.markdown('<div class="bento-card connectivity"><h3>Connectivity</h3><div class="content"><p>Sugestão de Exames</p></div></div>', unsafe_allow_html=True)
   
    row4_col1, row4_col2 = st.columns([4, 2])
    with row4_col1:
        with protection_content:
            st.markdown('<div class="bento-card protection" style="grid-column: span 2;"><h3>Protection</h3><div class="content"><p>Sugestão de Tratamento</p></div></div>', unsafe_allow_html=True)

    # 4. Adiciona o botão de Finalizar Consulta
    st.markdown("---")
    if st.button("⏹️ Finalizar Consulta", use_container_width=True, type="primary", key="finalizar_consulta_btn_bento"):
        decisao_final = st.session_state.get("prontuario_texto", "")
        if not decisao_final.strip():
            st.warning("Por favor, insira a sua decisão clínica final no campo de prontuário antes de finalizar.")
        else:
            st.session_state.decisao_a_finalizar = decisao_final
            st.session_state.etapa = 3
            st.rerun()