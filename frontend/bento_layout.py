# bento_layout.py

import streamlit as st

def render_bento_layout():
    """
    Renderiza o layout Bento Grid usando HTML e CSS injetados para
    máximo controle visual, conforme o modelo.
    """
    
    # Injeta o CSS e a estrutura HTML da grade
    st.markdown("""
    <style>
        /* Define a grade principal com 6 colunas para flexibilidade */
        .bento-grid-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            grid-auto-rows: minmax(150px, auto); /* Linhas com altura mínima de 150px */
            gap: 1rem;
            padding-top: 2rem;
        }

        /* Estilo base para cada bloco */
        .bento-card {
            background-color: #060010;
            border: 1px solid #332355;
            border-radius: 24px;
            padding: 1.5rem;
            color: #e0e0e0;
            display: flex;
            flex-direction: column;
            justify-content: space-between; /* Empurra o conteúdo para baixo */
        }
        
        .bento-card h3 {
            font-size: 0.9rem;
            color: #a79bbd;
            margin: 0;
            font-weight: 500;
        }
        
        .bento-card .content {
            font-size: 1.2rem;
            font-weight: 600;
        }

        /*
        Aqui está a mágica: definimos a área que cada bloco ocupa na grade.
        'grid-column: span X' -> faz o bloco ocupar X colunas.
        'grid-row: span Y' -> faz o bloco ocupar Y linhas.
        */
        .insights      { grid-column: span 2; grid-row: span 1; }
        .overview      { grid-column: span 2; grid-row: span 1; }
        .collaboration { grid-column: span 2; grid-row: span 2; } /* Ocupa 2 linhas de altura */
        .efficiency    { grid-column: span 4; grid-row: span 2; } /* Ocupa 4 colunas e 2 linhas */
        .connectivity  { grid-column: span 2; grid-row: span 1; }
        .protection    { grid-column: span 2; grid-row: span 1; }
    </style>

    <div class="bento-grid-container">
        <div class="bento-card insights">
            <h3>Insights</h3>
            <div class="content">Gravador e Transcrição</div>
        </div>
        
        <div class="bento-card overview">
            <h3>Overview</h3>
            <div class="content">Queixa Principal</div>
        </div>
        
        <div class="bento-card collaboration">
            <h3>Collaboration</h3>
            <div class="content">Documentos e Prontuário</div>
        </div>
        
        <div class="bento-card efficiency">
            <h3>Efficiency</h3>
            <div class="content">HDA, Antecedentes e Hipóteses</div>
        </div>
        
        <div class="bento-card connectivity">
            <h3>Connectivity</h3>
            <div class="content">Sugestão de Exames</div>
        </div>
        
        <div class="bento-card protection">
            <h3>Protection</h3>
            <div class="content">Sugestão de Tratamento</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # O botão de finalizar permanece fora da grade, por enquanto
    st.markdown("---")
    if st.button("⏹️ Finalizar Consulta", use_container_width=True, type="primary", key="finalizar_consulta_btn_bento"):
        decisao_final = st.session_state.get("prontuario_texto", "")
        if not decisao_final.strip():
            st.warning("Por favor, insira a sua decisão clínica final no campo de prontuário antes de finalizar.")
        else:
            st.session_state.decisao_a_finalizar = decisao_final
            st.session_state.etapa = 3
            st.rerun()