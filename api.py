# api.py

from fastapi import FastAPI
from pydantic import BaseModel
import os
import json

# Importamos toda a nossa lógica do ShaulaMed
from medico import Medico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console

# --- Inicialização do Servidor ---
app = FastAPI(
    title="ShaulaMed API",
    description="API para o copiloto clínico com IA reflexiva.",
    version="0.5.0"
)

# --- Objetos Globais ---
console = Console()
gerenciador = GerenciadorDeMedicos()
medico_logado = gerenciador.definir_medico_atual(
    nome_medico="Thalles Rodrigues",
    crm="12345-AM",
    especialidade="Otorrinolaringologia"
)

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    """
    Função SIMULADA de conexão com a LLM.
    Ela retorna respostas prontas para testarmos a hospedagem sem precisar de uma chave de API real.
    """
    console.print(f"\n[dim][API -> IA (SIMULADA): Núcleo de '{modo}' ativado...][/dim]")
    
    if modo == "Relatório Clínico":
        resposta_simulada = "[RELATÓRIO SIMULADO]: Análise da sessão gerada pela API online."
        return {"tipo": "texto", "conteudo": resposta_simulada}
    
    # Para o modo de Diagnóstico, retornamos uma string JSON, como a IA real faria.
    resposta_simulada_dict = {
        "hipoteses_diagnosticas": ["Hipótese (Gerada pela API Online)"],
        "sugestao_conduta": "Conduta (Gerada pela API Online).",
        "exames_sugeridos": ["Exame A (online)", "Exame B (online)"],
        "nivel_confianca_ia": "0.8"
    }
    return {"tipo": "texto", "conteudo": json.dumps(resposta_simulada_dict)}

# Criamos a instância principal do nosso agente, passando a função SIMULADA
agente = ShaulaMedAgent(
    medico=medico_logado, 
    console_log=console, 
    obter_resposta_llm_func=obter_resposta_llm_api
)

# --- Modelos de Dados Pydantic ---
class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str
    resumo: str

# --- Endpoints da API ---

@app.post("/consulta/iniciar", tags=["Consulta"])
def iniciar_consulta():
    agente.iniciar_nova_consulta()
    return {"status": "sucesso", "mensagem": "Nova consulta iniciada."}

@app.post("/consulta/processar", tags=["Consulta"])
def processar_fala(fala: FalaPaciente):
    if not agente.consulta_atual:
        return {"status": "erro", "mensagem": "Nenhuma consulta iniciada."}
    
    agente.processar_interacao(fala.texto)
    sugestao = agente.consulta_atual.sugestao_ia
    return {"status": "sucesso", "sugestao": sugestao}


# api.py (modifique o endpoint finalizar_consulta)

@app.post("/consulta/finalizar", tags=["Consulta"])
def finalizar_consulta(decisao: DecisaoFinal):
    if not agente.consulta_atual:
        return {"status": "erro", "mensagem": "Nenhuma consulta para finalizar."}
    
    encontro_finalizado = agente.consulta_atual
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    gerenciador.salvar_medicos()

    # --- MUDANÇA AQUI ---
    # Agora chamamos a nova função e usamos a chave "reflexao"
    reflexao = agente.gerar_reflexao_pos_consulta(encontro_finalizado, obter_resposta_llm_api)
    
    return {"status": "sucesso", "mensagem": "Consulta finalizada.", "reflexao": reflexao}
        

@app.get("/relatorio", tags=["Análise"])
def obter_relatorio():
    relatorio = agente.executar_analise_de_sessao(obter_resposta_llm_api)
    return {"status": "sucesso", "relatorio": relatorio}

# Adicione este novo endpoint no final do seu arquivo api.py

@app.get("/sessao/despedida", tags=["Sessão"])
def obter_despedida():
    """
    Gera e retorna a mensagem de despedida personalizada com base nas consultas do dia.
    """
    despedida = agente.gerar_despedida_do_dia(obter_resposta_llm_api)
    return {"status": "sucesso", "mensagem": despedida}