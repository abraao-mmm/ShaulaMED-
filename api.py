# api.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
import json
import openai
from typing import Dict

# Importamos TODAS as nossas classes
from medico import Medico
from encontro_clinico import EncontroClinico # <<< A LINHA QUE FALTAVA
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console

app = FastAPI(title="ShaulaMed API", version="3.1 - Stateless Fix")

console = Console()
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gerenciador = GerenciadorDeMedicos()
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização da API: {e}[/bold red]")

# (A sua função obter_resposta_llm_api permanece a mesma)
def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    # A sua lógica de conexão com a OpenAI vai aqui
    pass

# --- Sistema de Dependência e Gestão de Sessão ---
sessoes_de_consulta: Dict[str, EncontroClinico] = {}

def obter_agente_para_uid(uid: str) -> ShaulaMedAgent:
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": uid})
    if not perfil_medico:
        raise HTTPException(status_code=404, detail="Perfil do médico não encontrado para este UID.")
    return ShaulaMedAgent(medico=perfil_medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)

# (Os seus modelos Pydantic permanecem os mesmos)
class PerfilMedico(BaseModel):
    uid: str; email: str; nome_completo: str; apelido: str; crm: str; especialidade: str; sexo: str
class FalaPaciente(BaseModel):
    texto: str
class DecisaoFinal(BaseModel):
    decisao: str; resumo: str

# --- Endpoints ---

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.model_dump()
        dados_para_salvar.update({
            "id": perfil.uid, "nivel_confianca_ia": 1,
            "estilo_clinico_observado": {"padrao_prescritivo": {}, "exames_mais_solicitados": [], "linguagem_resumo": "SOAP"},
            "consultas_realizadas_count": 0
        })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consulta/iniciar/{uid}", tags=["Consulta"])
def iniciar_consulta(uid: str, agente: ShaulaMedAgent = Depends(obter_agente_para_uid)):
    agente.iniciar_nova_consulta()
    sessoes_de_consulta[uid] = agente.consulta_atual
    return {"status": "sucesso", "mensagem": "Nova consulta iniciada e guardada na sessão."}

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, fala: FalaPaciente, agente: ShaulaMedAgent = Depends(obter_agente_para_uid)):
    consulta_ativa = sessoes_de_consulta.get(uid)
    if not consulta_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma consulta iniciada.")
    agente.consulta_atual = consulta_ativa
    agente.processar_interacao(fala.texto)
    sessoes_de_consulta[uid] = agente.consulta_atual
    return {"status": "sucesso", "sugestao": agente.consulta_atual.sugestao_ia}

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, decisao: DecisaoFinal, agente: ShaulaMedAgent = Depends(obter_agente_para_uid)):
    consulta_ativa = sessoes_de_consulta.get(uid)
    if not consulta_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma consulta para finalizar.")
    agente.consulta_atual = consulta_ativa
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    reflexao = agente.gerar_reflexao_pos_consulta(consulta_ativa, obter_resposta_llm_api)
    if uid in sessoes_de_consulta:
        del sessoes_de_consulta[uid]
    return {"status": "sucesso", "reflexao": reflexao}