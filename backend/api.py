# api.py (Versão Completa e Estável)

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv
from typing import Dict, Optional
from datetime import datetime, timedelta

# Importações dos módulos do projeto
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from transcritor import transcrever_audio_bytes
from analise_clinica import MotorDeAnaliseClinica
from memoria_clinica import MemoriaClinica
from rich.console import Console
from gerador_documentos import GeradorDeDocumentos


# --- INICIALIZAÇÃO DA API E OBJETOS GLOBAIS ---
app = FastAPI(
    title="ShaulaMed API",
    description="API Stateless para o Copiloto Clínico ShaulaMed.",
    version="5.0 - Apoio à Decisão Clínica"
)
console = Console()

# --- CARREGAMENTO DE VARIÁVEIS DE AMBIENTE ---
load_dotenv() 

# --- INICIALIZAÇÃO DE SERVIÇOS ---
try:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        console.print("[bold red]AVISO: OPENAI_API_KEY não encontrada nas variáveis de ambiente.[/bold red]")
    gerenciador = GerenciadorDeMedicos()
except Exception as e:
    console.print(f"[bold red]ERRO CRÍTICO na inicialização da API: {e}[/bold red]")
    raise e

# --- FUNÇÃO DE CONEXÃO COM A LLM ---
def obter_resposta_llm_api(prompt: str, modo: str = "API") -> dict:
    console.print(f"\n[dim][API -> OpenAI: Núcleo de '{modo}' ativado...][/dim]")
    try:
        if not openai.api_key:
            raise ValueError("A chave de API da OpenAI não está configurada.")
        
        mensagens = [{"role": "user", "content": prompt}]
        response_format = {"type": "json_object"} if "json" in prompt.lower() else {"type": "text"}
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=mensagens,
            temperature=0.7,
            response_format=response_format
        )
        conteudo = response.choices[0].message.content.strip()
        return {"tipo": "texto", "conteudo": conteudo}
    except Exception as e:
        console.print(f"❌ [bold red]API: Erro na chamada da OpenAI: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=f"Erro na comunicação com a IA: {e}")

# --- MODELOS DE DADOS (PYDANTIC) ---
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

class ProcessarPayload(BaseModel):
    consulta_atual: dict
    fala: FalaPaciente

class FinalizarPayload(BaseModel):
    consulta_atual: dict
    decisao: DecisaoFinal
    formato_resumo: str

class DialogoResposta(BaseModel):
    texto_resposta: str

class DocumentoPayload(BaseModel):
    tipo_documento: str
    dados_consulta: dict


# --- ENDPOINTS DA API ---

@app.get("/", tags=["Status"])
def read_root():
    """Verifica se a API está online."""
    return {"status": "ShaulaMed API está online e funcional."}

@app.post("/sessao/ativar", tags=["Sessão"])
def ativar_sessao(user: UserSession):
    """Ativa uma sessão para um utilizador autenticado."""
    perfil_medico = gerenciador.carregar_ou_criar_perfil({"localId": user.uid, "email": user.email})
    if perfil_medico:
        return {"status": "sucesso", "mensagem": f"Sessão para Dr(a). {perfil_medico.apelido} validada."}
    raise HTTPException(status_code=404, detail="Não foi possível carregar ou criar o perfil do médico.")

@app.post("/medico/criar_perfil", tags=["Médico"])
def criar_perfil_medico(perfil: PerfilMedico):
    """Cria um novo perfil de médico no Firestore."""
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
    """Recebe um ficheiro de áudio e retorna a sua transcrição."""
    try:
        audio_bytes = await ficheiro_audio.read()
        texto = transcrever_audio_bytes(audio_bytes)
        if texto is not None:
            return {"status": "sucesso", "texto_transcrito": texto}
        raise HTTPException(status_code=400, detail="Não foi possível transcrever o áudio.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor de transcrição: {e}")

@app.post("/consulta/iniciar/{uid}", tags=["Consulta"])
def iniciar_consulta(uid: str):
    """Inicia uma nova consulta vazia para um médico."""
    nova_consulta = EncontroClinico(medico_id=uid, transcricao_consulta="")
    return nova_consulta.para_dict()

@app.post("/consulta/processar/{uid}", tags=["Consulta"])
def processar_fala(uid: str, payload: ProcessarPayload):
    """Processa a fala transcrita, gera a nota estruturada e a análise avançada."""
    medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    agente = ShaulaMedAgent(medico=medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)
    agente.consulta_atual = EncontroClinico.de_dict(payload.consulta_atual)
    agente.processar_interacao(payload.fala.texto)
    return agente.consulta_atual.para_dict()

@app.post("/consulta/finalizar/{uid}", tags=["Consulta"])
def finalizar_consulta(uid: str, payload: FinalizarPayload):
    """Finaliza a consulta, gera o resumo para prontuário e a reflexão, e retorna ambos."""
    medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    
    agente = ShaulaMedAgent(medico=medico, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm_api)
    agente.consulta_atual = EncontroClinico.de_dict(payload.consulta_atual)
    
    resultado_finalizacao = agente.finalizar_consulta(
        decisao_medico_final=payload.decisao.decisao,
        obter_resposta_llm_func=obter_resposta_llm_api,
        formato_resumo=payload.formato_resumo
    )
    
    return {"status": "sucesso", **resultado_finalizacao}

@app.get("/medico/{uid}/relatorio_semanal", tags=["Relatórios"])
def get_relatorio_semanal(uid: str):
    """Gera e retorna o relatório semanal de performance para um médico."""
    try:
        medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
        if not medico:
            raise HTTPException(status_code=404, detail="Médico não encontrado.")
        
        memoria = MemoriaClinica(medico_id=uid)
        
        uma_semana_atras = datetime.now() - timedelta(days=7)
        consultas_da_semana = [
            enc for enc in memoria.encontros_em_memoria 
            if enc.timestamp >= uma_semana_atras
        ]
        
        motor_analise = MotorDeAnaliseClinica()
        
        relatorio_completo = motor_analise.gerar_relatorio_semanal_completo(
            encontros=consultas_da_semana,
            nome_medico=medico.apelido,
            obter_resposta_llm_func=obter_resposta_llm_api
        )
        
        return relatorio_completo
        
    except Exception as e:
        console.print(f"❌ [bold red]Erro ao gerar relatório semanal: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar o relatório: {e}")

@app.post("/consulta/{consulta_id}/salvar_reflexao_medico", tags=["Relatórios"])
def salvar_reflexao_medico(consulta_id: str, resposta: DialogoResposta, uid: str):
    """Salva a reflexão escrita pelo médico sobre um caso específico no Firestore."""
    console.print(f"[{uid}] Salvando resposta do diálogo para a consulta {consulta_id}...")
    try:
        consulta_ref = gerenciador.medicos_ref.document(uid).collection('consultas').document(consulta_id)
        consulta_ref.update({
            "reflexao_medico": resposta.texto_resposta
        })
        return {"status": "sucesso", "mensagem": "Reflexão salva com sucesso."}
    except Exception as e:
        console.print(f"❌ [bold red]Erro ao salvar reflexão do médico: {e}[/bold red]")
        raise HTTPException(status_code=500, detail=f"Erro interno ao salvar a reflexão: {e}")
    
# 3. Adicionar o novo endpoint
@app.post("/consulta/gerar_documento/{uid}", tags=["Documentos"])
def gerar_documento_clinico(uid: str, payload: DocumentoPayload):
    """
    Gera um documento clínico (receita, atestado, etc.) com base nos dados da consulta.
    """
    # Carrega o perfil do médico para obter nome, CRM, etc.
    medico = gerenciador.carregar_ou_criar_perfil({"localId": uid, "email": ""})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    
    dados_medico = {
        "nome_completo": medico.nome_completo,
        "crm": medico.crm,
        "especialidade": medico.especialidade
    }

    # Instancia o gerador de documentos
    gerador = GeradorDeDocumentos(obter_resposta_llm_api)
    
    # Gera o documento
    documento_texto = gerador.gerar_documento(
        tipo_documento=payload.tipo_documento,
        dados_consulta=payload.dados_consulta,
        dados_medico=dados_medico
    )
    
    if "Não foi possível" in documento_texto:
        raise HTTPException(status_code=500, detail=documento_texto)

    return {"documento_gerado": documento_texto}    