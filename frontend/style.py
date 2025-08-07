# style.py

import streamlit as st

def get_css():
    """
    Retorna o CSS completo para o layout Bento Grid.
    """
    return """
    <style>
        /* Remove o espaçamento extra criado pelo Streamlit nos blocos verticais */
        .stApp [data-testid="stVerticalBlock"] .st-emotion-cache-1jicfl2 {
            gap: 0rem;
        }

        /* Container principal do Bento Grid */
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr); /* Cria 6 colunas de largura igual */
            grid-auto-rows: minmax(100px, auto); /* Altura mínima para as linhas */
            gap: 1rem;
            width: 100%;
            max-width: 1000px;
            margin: 2rem auto;
        }

        /* Estilo base para cada bloco */
        .bento-card {
            background-color: #060010;
            border: 1px solid #332355;
            border-radius: 16px;
            padding: 1.5rem;
            color: #e0e0e0;
            display: flex;
            flex-direction: column;
            justify-content: space-between; /* Espaça o título do conteúdo */
            position: relative; /* Necessário para posicionamento de elementos internos */
            overflow: hidden; /* Garante que os conteúdos não ultrapassem as bordas */
        }
        .bento-card h3 {
            font-size: 0.9rem;
            color: #a79bbd;
            margin: 0;
            font-weight: 500;
        }
        .bento-card .content {
            font-size: 1rem;
            font-weight: 600;
        }
        .bento-card .streamlit-expanderHeader {
            padding: 0;
        }

        /* Definindo a posição e o tamanho de cada bloco na grade */
        .insights      { grid-column: span 2; grid-row: span 1; }
        .overview      { grid-column: span 2; grid-row: span 1; }
        .collaboration { grid-column: span 2; grid-row: span 2; }
        .efficiency    { grid-column: span 4; grid-row: span 2; }
        .connectivity  { grid-column: span 2; grid-row: span 1; }
        .protection    { grid-column: span 2; grid-row: span 1; }

    </style>
    """