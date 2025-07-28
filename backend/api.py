# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
import os
import json
import openai
from dotenv import load_dotenv
from typing import Dict, Callable

# Carrega as variáveis do ficheiro .env para o ambiente (para testes locais)
load_dotenv()

# Importamos a nossa lógica do ShaulaMed e as ferramentas necessárias
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from rich.console import Console

# --- INICIALIZAÇÃO DA API E OBJETOS GLOBAIS ---
app = FastAPI(title="ShaulaMed API", version="3.3 - Final Sync")

console = Console()

# --- CONEXÃO SEGURA COM A OPENAI ---
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gerenciador = GerenciadorDeMedicos()
    if not openai.api_key:
        console.print("[bold red]AVISO: OPENAI_API_KEY não encontrada.[/bold red]")
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização: {e}[/bold red]")

# "Memória de curto prazo" para as sessões
agentes_ativos: Dict[str, ShaulaMedAgent] = {}
sessoes_de_consulta: Dict[str, EncontroClinico] = {}

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    # A sua lógica de conexão com a OpenAI vai aqui
    pass

# --- MODELOS DE DADOS PYDANTIC ---
class UserSession(BaseModel):
    uid: str; email: str

class PerfilMedico(BaseModel):
    uid: str; email: str; nome_completo: str; apelido: str; crm: str; especialidade: str; sexo: str

class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str; resumo: str

# --- ENDPOINTS DA API ---

@app.post("/sessao/ativar", tags=["Sessão"])
def ativar_sessao(user: UserSession):
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": user.uid, "email": user.email})
    if perfil_medico:
        agentes_ativos[user.uid] = ShaulaMedAgent(medico=perfil_medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)
        return {"status": "sucesso", "mensagem": f"Agente para Dr(a). {perfil_medico.apelido} ativado."}
    raise HTTPException(status_code=404, detail="Não foi possível carregar ou criar o perfil do médico.")

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.model_dump()
        dados_para_salvar.update({ "id": perfil.uid, "nivel_confianca_ia": 1, "estilo_clinico_observado": {"padrao_prescritivo": {}, "exames_mais_solicitados": []}, "consultas_realizadas_count": 0 })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audio/transcrever", tags=["Áudio"])
async def endpoint_transcrever_audio(ficheiro_audio: UploadFile = File(...)):
    try:
        audio_bytes = await ficheiro_audio.read()
        texto = transcrever_audio_bytes(audio_bytes)
        if texto is not None:
            return {"status": "sucesso", "texto_transcrito": texto}
        else:
            raise HTTPException(status_code=400, detail="Não foi possível transcrever o áudio.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor de transcrição: {e}")

@app.post("/consulta/iniciar/{uid}", tags=["Consulta"])
def iniciar_consulta(uid: str):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão não encontrada. Por favor, ative a sessão novamente.")
    agente.iniciar_nova_consulta()
    sessoes_de_consulta[uid] = agente.consulta_atual
    return {"status": "sucesso"}

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, fala: FalaPaciente):
    agente = agentes_ativos.get(uid)
    consulta_ativa = sessoes_de_consulta.get(uid)
    if not agente or not consulta_ativa: raise HTTPException(status_code=400, detail="Consulta não iniciada ou sessão inválida.")
    agente.consulta_atual = consulta_ativa
    agente.processar_interacao(fala.texto)
    sessoes_de_consulta[uid] = agente.consulta_atual
    return {"status": "sucesso", "sugestao": agente.consulta_atual.sugestao_ia}

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, decisao: DecisaoFinal):
    agente = agentes_ativos.get(uid)
    consulta_ativa = sessoes_de_consulta.get(uid)
    if not agente or not consulta_ativa: raise HTTPException(status_code=400, detail="Consulta não iniciada ou sessão inválida.")
    agente.consulta_atual = consulta_ativa
    reflexao = agente.gerar_reflexao_pos_consulta(agente.consulta_atual, obter_resposta_llm_api)
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    if uid in sessoes_de_consulta:
        del sessoes_de_consulta[uid]
    return {"status": "sucesso", "reflexao": reflexao}