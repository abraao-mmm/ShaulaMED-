# api.py

from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import openai # Supondo que usaremos OpenAI no futuro

# Importamos toda a nossa lógica do ShaulaMed
from medico import Medico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console

# --- Inicialização do Servidor ---
app = FastAPI(
    title="ShaulaMed API",
    description="API para o copiloto clínico com IA reflexiva.",
    version="1.0"
)

# --- Objetos Globais ---
console = Console()
gerenciador = GerenciadorDeMedicos()
# Já não definimos um "medico_logado" aqui, pois a autenticação tratará disso.
# O agente será instanciado conforme a necessidade ou numa futura lógica de sessão.

# (A sua função obter_resposta_llm_api viria aqui, seja a simulada ou a real)
def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    # Lógica de conexão com a IA (simulada ou real com OpenAI/Groq)
    pass 

# Por agora, vamos criar um agente genérico na inicialização
medico_exemplo = gerenciador.definir_medico_atual("Dr. Teste", "0000", "Geral")
agente = ShaulaMedAgent(
    medico=medico_exemplo, 
    console_log=console, 
    obter_resposta_llm_func=obter_resposta_llm_api
)


# --- Modelos de Dados Pydantic ---
class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str
    resumo: str

class PerfilMedico(BaseModel):
    uid: str
    email: str
    nome_completo: str
    apelido: str
    crm: str
    especialidade: str
    sexo: str


# --- Endpoints da API ---

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    """
    Recebe os dados de um novo médico e cria o seu perfil no Firestore.
    """
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.dict() # Pydantic converte o modelo para dict
        # Adicionamos campos que não vêm do formulário
        dados_para_salvar.update({
            "id": perfil.uid,
            "nivel_confianca_ia": 1,
            "estilo_clinico_observado": {
                "padrao_prescritivo": {}, "exames_mais_solicitados": [], "linguagem_resumo": "SOAP"
            },
            "consultas_realizadas_count": 0
        })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso", "mensagem": "Perfil do médico criado no Firestore."}
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao criar perfil no Firestore: {e}"}

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

@app.post("/consulta/finalizar", tags=["Consulta"])
def finalizar_consulta(decisao: DecisaoFinal):
    if not agente.consulta_atual:
        return {"status": "erro", "mensagem": "Nenhuma consulta para finalizar."}
    encontro_finalizado = agente.consulta_atual
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    # A lógica de salvar o médico agora é tratada na criação do perfil
    reflexao = agente.gerar_reflexao_pos_consulta(encontro_finalizado, obter_resposta_llm_api)
    return {"status": "sucesso", "mensagem": "Consulta finalizada.", "reflexao": reflexao}

@app.get("/relatorio", tags=["Análise"])
def obter_relatorio():
    relatorio = agente.executar_analise_de_sessao(obter_resposta_llm_api)
    return {"status": "sucesso", "relatorio": relatorio}

@app.get("/sessao/despedida", tags=["Sessão"])
def obter_despedida():
    despedida = agente.gerar_despedida_do_dia(obter_resposta_llm_api)
    return {"status": "sucesso", "mensagem": despedida}