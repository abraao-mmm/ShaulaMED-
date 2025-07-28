# api.py (VERSÃO REATORADA - STATELESS)

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv
from typing import Dict, Optional

# Carrega as variáveis de ambiente
load_dotenv()

# Importações dos módulos do projeto
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from rich.console import Console

# --- INICIALIZAÇÃO DA API E OBJETOS GLOBAIS ---
app = FastAPI(
    title="ShaulaMed API",
    description="API Stateless para o Copiloto Clínico ShaulaMed.",
    version="4.0 - Stateless"
)
console = Console()

# --- INICIALIZAÇÃO DE SERVIÇOS ---
# O gerenciador de médicos e a chave da API são inicializados uma vez.
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        console.print("[bold red]AVISO: OPENAI_API_KEY não encontrada.[/bold red]")
    gerenciador = GerenciadorDeMedicos()
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização da API: {e}[/bold red]")
    # Em caso de erro crítico na inicialização, a API não deve iniciar.
    raise e

# --- FUNÇÃO DE CONEXÃO COM A LLM ---
def obter_resposta_llm_api(prompt: str, modo: str = "API") -> dict:
    """Função que se conecta à API da OpenAI para obter respostas."""
    console.print(f"\n[dim][API -> OpenAI: Núcleo de '{modo}' ativado...][/dim]")
    try:
        if not openai.api_key:
            raise ValueError("A chave de API da OpenAI não está configurada.")
        
        mensagens = [{"role": "user", "content": prompt}]
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=mensagens,
            temperature=0.7,
            response_format={"type": "json_object"} if "json" in prompt.lower() else {"type": "text"}
        )
        conteudo = response.choices[0].message.content.strip()
        return {"tipo": "texto", "conteudo": conteudo}
    except Exception as e:
        console.print(f"❌ [bold red]API: Erro na chamada da OpenAI: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=f"Erro na comunicação com a IA: {e}")

# --- MODELOS DE DADOS (PYDANTIC) PARA AS REQUISIÇÕES ---
class UserSession(BaseModel):
    uid: str
    email: str

class PerfilMedico(BaseModel):
    uid: str; email: str; nome_completo: str; apelido: str; crm: str; especialidade: str; sexo: str

class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str
    resumo: str

# Modelos para a arquitetura stateless
class ProcessarPayload(BaseModel):
    consulta_atual: dict
    fala: FalaPaciente

class FinalizarPayload(BaseModel):
    consulta_atual: dict
    decisao: DecisaoFinal

# --- ENDPOINTS DA API (REATORADOS) ---

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ShaulaMed API está online e funcional."}

@app.post("/sessao/ativar", tags=["Sessão"])
def ativar_sessao(user: UserSession):
    """Verifica se o perfil do médico existe. Não guarda mais estado na memória."""
    console.print(f"Ativando sessão para UID: {user.uid}")
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": user.uid, "email": user.email})
    if perfil_medico:
        return {"status": "sucesso", "mensagem": f"Sessão para Dr(a). {perfil_medico.apelido} validada."}
    raise HTTPException(status_code=404, detail="Não foi possível carregar ou criar o perfil do médico.")

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    """Cria o perfil do médico no Firestore. Endpoint já era stateless."""
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.model_dump()
        dados_para_salvar.update({
            "id": perfil.uid, "nivel_confianca_ia": 1,
            "estilo_clinico_observado": {"padrao_prescritivo": {}, "exames_mais_solicitados": []},
            "consultas_realizadas_count": 0
        })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso", "mensagem": "Perfil criado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audio/transcrever", tags=["Áudio"])
async def endpoint_transcrever_audio(ficheiro_audio: UploadFile = File(...)):
    """Transcreve áudio usando Whisper. Endpoint já era stateless."""
    try:
        audio_bytes = await ficheiro_audio.read()
        texto = transcrever_audio_bytes(audio_bytes)
        if texto is not None:
            return {"status": "sucesso", "texto_transcrito": texto}
        raise HTTPException(status_code=400, detail="Não foi possível transcrever o áudio.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor de transcrição: {e}")

# --- NOVOS ENDPOINTS DE CONSULTA (STATELESS) ---

@app.post("/consulta/iniciar/{uid}", tags=["Consulta"])
def iniciar_consulta(uid: str):
    """Cria um objeto de consulta em branco e o retorna para o front-end."""
    console.print(f"[{uid}] Nova consulta iniciada.")
    nova_consulta = EncontroClinico(medico_id=uid, transcricao_consulta="")
    return nova_consulta.para_dict()

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, payload: ProcessarPayload):
    """Recebe o estado da consulta, processa e retorna o estado atualizado."""
    console.print(f"[{uid}] Processando fala...")
    # 1. Carrega o perfil do médico e instancia o agente na hora
    medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    
    agente = ShaulaMedAgent(medico=medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)
    
    # 2. Hidrata o estado da consulta a partir do que o front-end enviou
    agente.consulta_atual = EncontroClinico.de_dict(payload.consulta_atual)
    
    # 3. Processa a nova interação
    agente.processar_interacao(payload.fala.texto)
    
    # 4. Retorna o objeto da consulta totalmente atualizado
    return agente.consulta_atual.para_dict()

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, payload: FinalizarPayload):
    """Recebe o estado final da consulta, salva no banco e retorna a reflexão."""
    console.print(f"[{uid}] Finalizando consulta...")
    # 1. Carrega o perfil e instancia o agente
    medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")

    agente = ShaulaMedAgent(medico=medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)
    
    # 2. Hidrata o estado da consulta
    agente.consulta_atual = EncontroClinico.de_dict(payload.consulta_atual)
    
    # 3. Gera a reflexão ANTES de finalizar e limpar os dados
    reflexao = agente.gerar_reflexao_pos_consulta(agente.consulta_atual, obter_resposta_llm_api)
    
    # 4. Finaliza a consulta (salva no Firestore)
    agente.finalizar_consulta(payload.decisao.decisao, payload.decisao.resumo)
    
    return {"status": "sucesso", "reflexao": reflexao}