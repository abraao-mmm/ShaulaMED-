# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
import os
import json
import openai
from typing import Dict, Callable

# Carrega as variáveis do ficheiro .env para o ambiente (para testes locais)
from dotenv import load_dotenv
load_dotenv()

# Importamos a nossa lógica do ShaulaMed
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from rich.console import Console

# --- INICIALIZAÇÃO DA API E OBJETOS GLOBAIS ---
app = FastAPI(title="ShaulaMed API", version="3.2 - Final")
console = Console()

# --- MODELOS DE DADOS PYDANTIC (DEFINIDOS PRIMEIRO) ---
class UserSession(BaseModel):
    uid: str
    email: str

class PerfilMedico(BaseModel):
    uid: str
    email: str
    nome_completo: str
    apelido: str
    crm: str
    especialidade: str
    sexo: str

class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str
    resumo: str

# --- CONFIGURAÇÃO DA CONEXÃO COM A IA E FIREBASE ---
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gerenciador = GerenciadorDeMedicos()
    if not openai.api_key:
        console.print("[bold red]AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.[/bold red]")
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização: {e}[/bold red]")

# "Memória de curto prazo" para as sessões de consulta ativas
sessoes_de_consulta: Dict[str, EncontroClinico] = {}

# --- FUNÇÕES AUXILIARES E DE DEPENDÊNCIA ---

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    # ... (A sua função de conexão com a OpenAI permanece a mesma)
    pass

def obter_agente_para_uid(uid: str) -> ShaulaMedAgent:
    """Carrega o perfil do médico e cria uma instância do agente para o pedido."""
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": uid})
    if not perfil_medico:
        raise HTTPException(status_code=404, detail="Perfil do médico não encontrado para este UID.")
    return ShaulaMedAgent(medico=perfil_medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)

# --- ENDPOINTS DA API ---

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
    return {"status": "sucesso"}

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