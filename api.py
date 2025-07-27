# api.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import json
import openai
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console

app = FastAPI(title="ShaulaMed API", version="3.3 - Final Sync")
console = Console()

try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    gerenciador = GerenciadorDeMedicos()
    if not openai.api_key:
        console.print("[bold red]AVISO: OPENAI_API_KEY não encontrada.[/bold red]")
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização: {e}[/bold red]")

agentes_ativos: Dict[str, ShaulaMedAgent] = {}
sessoes_de_consulta: Dict[str, EncontroClinico] = {}

# api.py

# ... (o resto das suas importações e código da API)

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    """
    Função REAL que se conecta à API da OpenAI para obter respostas.
    """
    console.print(f"\n[dim][API -> OpenAI: Núcleo de '{modo}' ativado...][/dim]")
    try:
        # Verifica se a chave de API foi carregada do ambiente do Render
        if not openai.api_key:
            raise ValueError("A chave de API da OpenAI não está configurada no ambiente do servidor.")

        mensagens = [{"role": "user", "content": prompt}]
        
        # O FastAPI/Pydantic lida com a validação do schema, aqui apenas dizemos à OpenAI para usar o modo JSON
        response_format = {"type": "json_object"} if schema else {"type": "text"}

        # Faz a chamada para a API da OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o",  # Usamos o modelo mais recente e poderoso
            messages=mensagens,
            temperature=0.7,
            response_format=response_format
        )
        
        conteudo = response.choices[0].message.content.strip()
        
        # Envolve a resposta num formato padronizado para o resto do nosso sistema
        return {"tipo": "texto", "conteudo": conteudo}

    except Exception as e:
        console.print(f"❌ [bold red]API: Erro na chamada da OpenAI: {e}[/bold red]")
        # Retorna uma resposta de erro padronizada
        return {"tipo": "erro", "conteudo": "{}"}

# ... (o resto dos seus endpoints /consulta/iniciar, etc.)

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