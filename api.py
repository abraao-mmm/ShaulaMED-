# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import json
import openai
from typing import Dict, Callable

from medico import Medico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from rich.console import Console

app = FastAPI(title="ShaulaMed API", version="3.0 - Final")

console = Console()
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gerenciador = GerenciadorDeMedicos()
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização da API: {e}[/bold red]")

agentes_ativos: Dict[str, ShaulaMedAgent] = {}

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    try:
        if not openai.api_key:
            return {"tipo": "erro", "conteudo": "Chave da API da OpenAI não configurada."}
        mensagens = [{"role": "user", "content": prompt}]
        response_format = {"type": "json_object"} if schema else {"type": "text"}
        response = openai.chat.completions.create(model="gpt-4o", messages=mensagens, temperature=0.7, response_format=response_format)
        return {"tipo": "texto", "conteudo": response.choices[0].message.content.strip()}
    except Exception as e:
        console.print(f"❌ Erro na chamada da OpenAI: {e}")
        return {"tipo": "erro", "conteudo": "{}"}

class UserSession(BaseModel):
    uid: str; email: str
class PerfilMedico(BaseModel):
    uid: str; email: str; nome_completo: str; apelido: str; crm: str; especialidade: str; sexo: str
class FalaPaciente(BaseModel):
    texto: str
class DecisaoFinal(BaseModel):
    decisao: str; resumo: str

@app.post("/sessao/ativar", tags=["Sessão"])
def ativar_sessao(user: UserSession):
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": user.uid, "email": user.email})
    if perfil_medico:
        agentes_ativos[user.uid] = ShaulaMedAgent(
            medico=perfil_medico, 
            gerenciador=gerenciador,
            console_log=console, 
            obter_resposta_llm_func=obter_resposta_llm_api
        )
        return {"status": "sucesso", "mensagem": f"Agente para Dr(a). {perfil_medico.apelido} ativado."}
    raise HTTPException(status_code=404, detail="Perfil do médico não encontrado.")

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
def iniciar_consulta(uid: str):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão não encontrada. Por favor, ative a sessão novamente.")
    agente.iniciar_nova_consulta()
    return {"status": "sucesso"}

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, fala: FalaPaciente):
    agente = agentes_ativos.get(uid)
    if not agente or not agente.consulta_atual: raise HTTPException(status_code=400, detail="Consulta não iniciada ou sessão inválida.")
    agente.processar_interacao(fala.texto)
    return {"status": "sucesso", "sugestao": agente.consulta_atual.sugestao_ia}

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, decisao: DecisaoFinal):
    agente = agentes_ativos.get(uid)
    if not agente or not agente.consulta_atual: raise HTTPException(status_code=400, detail="Consulta não iniciada ou sessão inválida.")
    encontro = agente.consulta_atual
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    reflexao = agente.gerar_reflexao_pos_consulta(encontro, obter_resposta_llm_api)
    return {"status": "sucesso", "reflexao": reflexao}

@app.get("/relatorio/{uid}", tags=["Análise"])
def obter_relatorio(uid: str):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    relatorio = agente.executar_analise_de_sessao(obter_resposta_llm_api)
    return {"status": "sucesso", "relatorio": relatorio}

@app.get("/sessao/despedida/{uid}", tags=["Sessão"])
def obter_despedida(uid: str):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    despedida = agente.gerar_despedida_do_dia(obter_resposta_llm_api)
    return {"status": "sucesso", "mensagem": despedida}