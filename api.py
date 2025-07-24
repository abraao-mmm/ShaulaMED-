from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import openai # Supondo OpenAI
from medico import Medico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console
from typing import Dict

app = FastAPI(title="ShaulaMed API", version="2.0")

console = Console()
gerenciador = GerenciadorDeMedicos()
agentes_ativos: Dict[str, ShaulaMedAgent] = {}

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    # A sua lógica de conexão com a IA (OpenAI, Groq, etc.) vai aqui.
    # Esta é uma versão simulada para garantir que tudo funciona.
    print(f"API: Enviando prompt para a LLM no modo '{modo}'...")
    if modo == "Relatório Clínico":
        return {"tipo": "texto", "conteudo": "[RELATÓRIO SIMULADO]: Análise gerada pela API."}
    if modo == "Reflexão Pós-Consulta":
        return {"tipo": "texto", "conteudo": "Reflexão simulada sobre a consulta."}
    return {"tipo": "texto", "conteudo": json.dumps({"hipoteses_diagnosticas": ["Hipótese da API"]})}

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

# --- Endpoints ---

@app.post("/sessao/ativar", tags=["Sessão"])
def ativar_sessao(user: UserSession):
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": user.uid, "email": user.email})
    if perfil_medico:
        agentes_ativos[user.uid] = ShaulaMedAgent(
            medico=perfil_medico, 
            console_log=console, 
            obter_resposta_llm_func=obter_resposta_llm_api
        )
        return {"status": "sucesso", "mensagem": f"Agente para Dr(a). {perfil_medico.apelido} ativado."}
    raise HTTPException(status_code=404, detail="Perfil do médico não encontrado no Firestore.")

# --- O ENDPOINT QUE ESTÁ A FALTAR NO SERVIDOR ---
@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.dict()
        dados_para_salvar.update({
            "id": perfil.uid, "nivel_confianca_ia": 1,
            "estilo_clinico_observado": {"padrao_prescritivo": {}, "exames_mais_solicitados": [], "linguagem_resumo": "SOAP"},
            "consultas_realizadas_count": 0
        })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso", "mensagem": "Perfil do médico criado no Firestore."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar perfil no Firestore: {e}")

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    try:
        medico_doc_ref = gerenciador.medicos_ref.document(perfil.uid)
        dados_para_salvar = perfil.dict()
        dados_para_salvar.update({
            "id": perfil.uid, "nivel_confianca_ia": 1,
            "estilo_clinico_observado": {"padrao_prescritivo": {}, "exames_mais_solicitados": [], "linguagem_resumo": "SOAP"},
            "consultas_realizadas_count": 0
        })
        medico_doc_ref.set(dados_para_salvar)
        return {"status": "sucesso", "mensagem": "Perfil do médico criado no Firestore."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar perfil no Firestore: {e}")

# --- Endpoints da Aplicação (Agora precisam do UID) ---

@app.post("/consulta/iniciar/{uid}", tags=["Consulta"])
def iniciar_consulta(uid: str):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão do utilizador não encontrada. Por favor, faça o login novamente.")
    agente.iniciar_nova_consulta()
    return {"status": "sucesso", "mensagem": "Nova consulta iniciada."}

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, fala: FalaPaciente):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão do utilizador não encontrada.")
    if not agente.consulta_atual: raise HTTPException(status_code=400, detail="Nenhuma consulta iniciada.")
    agente.processar_interacao(fala.texto)
    return {"status": "sucesso", "sugestao": agente.consulta_atual.sugestao_ia}

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, decisao: DecisaoFinal):
    agente = agentes_ativos.get(uid)
    if not agente: raise HTTPException(status_code=404, detail="Sessão do utilizador não encontrada.")
    if not agente.consulta_atual: raise HTTPException(status_code=400, detail="Nenhuma consulta para finalizar.")
    encontro_finalizado = agente.consulta_atual
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    reflexao = agente.gerar_reflexao_pos_consulta(encontro_finalizado, obter_resposta_llm_api)
    return {"status": "sucesso", "mensagem": "Consulta finalizada.", "reflexao": reflexao}