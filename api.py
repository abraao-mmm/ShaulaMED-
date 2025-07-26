# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
import os
import json
import openai
from typing import Dict, Callable

# Importamos a nossa lógica do ShaulaMed
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from rich.console import Console

# --- INICIALIZAÇÃO E CONFIGURAÇÃO DA API ---
app = FastAPI(title="ShaulaMed API", version="3.0 - Stateless Final")

console = Console()

# --- CONEXÃO SEGURA COM A OPENAI ---
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        console.print("[bold red]AVISO: A variável de ambiente OPENAI_API_KEY não foi encontrada.[/bold red]")
except Exception as e:
    console.print(f"[bold red]Erro ao configurar o cliente OpenAI: {e}[/bold red]")

# --- OBJETOS GLOBAIS ---
# O gerenciador é criado uma vez, quando a API inicia
gerenciador = GerenciadorDeMedicos()
# Dicionário para guardar em cache as sessões de consulta ativas
sessoes_de_consulta: Dict[str, EncontroClinico] = {}

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    """Função REAL que se conecta à API da OpenAI para obter respostas."""
    console.print(f"\n[dim][API -> OpenAI: Núcleo de '{modo}' ativado...][/dim]")
    try:
        if not openai.api_key:
            raise ValueError("A chave de API da OpenAI não está configurada.")
        mensagens = [{"role": "user", "content": prompt}]
        response_format = {"type": "json_object"} if schema else {"type": "text"}
        response = openai.chat.completions.create(model="gpt-4o", messages=mensagens, temperature=0.7, response_format=response_format)
        return {"tipo": "texto", "conteudo": response.choices[0].message.content.strip()}
    except Exception as e:
        console.print(f"❌ [bold red]API: Erro na chamada da OpenAI: {e}[/bold red]")
        return {"tipo": "erro", "conteudo": "{}"}

# --- Sistema de Dependência para obter o Agente ---
def obter_agente_para_uid(uid: str) -> ShaulaMedAgent:
    """
    Esta é a nossa função "stateless". Para cada pedido que a precisa,
    ela carrega o perfil do médico e cria uma nova instância do agente.
    """
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": uid})
    if not perfil_medico:
        raise HTTPException(status_code=404, detail="Perfil do médico não encontrado para este UID.")
    return ShaulaMedAgent(medico=perfil_medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)

# --- MODELOS DE DADOS PYDANTIC ---
class PerfilMedico(BaseModel):
    uid: str; email: str; nome_completo: str; apelido: str; crm: str; especialidade: str; sexo: str
class FalaPaciente(BaseModel):
    texto: str
class DecisaoFinal(BaseModel):
    decisao: str; resumo: str

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
def iniciar_consulta(uid: str, agente: ShaulaMedAgent = Depends(obter_agente_para_uid)):
    agente.iniciar_nova_consulta()
    sessoes_de_consulta[uid] = agente.consulta_atual
    return {"status": "sucesso", "mensagem": "Nova consulta iniciada e guardada na sessão."}

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, fala: FalaPaciente, agente: ShaulaMedAgent = Depends(obter_agente_para_uid)):
    consulta_ativa = sessoes_de_consulta.get(uid)
    if not consulta_ativa:
        raise HTTPException(status_code=400, detail="Nenhuma consulta iniciada. Por favor, inicie uma nova consulta.")
    agente.consulta_atual = consulta_ativa
    agente.processar_interacao(fala.texto)
    sessoes_de_consulta[uid] = agente.consulta_atual # Atualiza a sessão com os novos dados
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
        del sessoes_de_consulta[uid] # Limpa a sessão da consulta ativa
    return {"status": "sucesso", "reflexao": reflexao}