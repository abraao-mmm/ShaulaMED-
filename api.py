# api.py

from fastapi import FastAPI
from pydantic import BaseModel
import openai
import json

# Importamos toda a nossa lógica do ShaulaMed
from medico import Medico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console

# --- Inicialização do Servidor ---
app = FastAPI(
    title="ShaulaMed API",
    description="API para o copiloto clínico com IA reflexiva.",
    version="0.5.0"
)

# --- Objetos Globais ---
# Estes objetos são criados uma vez, quando o servidor liga,
# e permanecem na memória para atender a todas as requisições.
console = Console()
gerenciador = GerenciadorDeMedicos()
medico_logado = gerenciador.definir_medico_atual(
    nome_medico="Thalles Rodrigues",
    crm="12345-AM",
    especialidade="Otorrinolaringologia"
)

def obter_resposta_llm_api(prompt: str, modo: str = "API", schema: dict = None) -> dict:
    """Função real de conexão com a LLM para ser usada pela API."""
    console.print(f"\n[dim][API -> IA: Núcleo de '{modo}' ativado...][/dim]")
    MODELO_USADO = "lmstudio-community/Phi-3-mini-4k-instruct-gguf" # Verifique o nome do seu modelo
    
    mensagens = [{"role": "user", "content": prompt}]
    
    if schema:
        system_prompt = f"Responda em formato JSON seguindo este schema: {json.dumps(schema)}"
        mensagens.insert(0, {"role": "system", "content": system_prompt})

    try:
        client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        response = client.chat.completions.create(
            model=MODELO_USADO,
            messages=mensagens,
            temperature=0.7,
        )
        conteudo = response.choices[0].message.content.strip()
        return {"tipo": "texto", "conteudo": conteudo}
    except Exception as e:
        console.print(f"❌ [bold red]API: Erro na chamada da IA: {e}[/bold red]")
        return {"tipo": "erro", "conteudo": "{}"}

# Criamos a instância principal do nosso agente, passando a função real da LLM
agente = ShaulaMedAgent(
    medico=medico_logado, 
    console_log=console, 
    obter_resposta_llm_func=obter_resposta_llm_api
)

# --- Modelos de Dados Pydantic ---
# Definem a estrutura dos dados que a API espera receber
class FalaPaciente(BaseModel):
    texto: str

class DecisaoFinal(BaseModel):
    decisao: str
    resumo: str

# --- Endpoints da API ---

@app.post("/consulta/iniciar", tags=["Consulta"])
def iniciar_consulta():
    """Inicia uma nova sessão de consulta no agente."""
    agente.iniciar_nova_consulta()
    return {"status": "sucesso", "mensagem": "Nova consulta iniciada."}

@app.post("/consulta/processar", tags=["Consulta"])
def processar_fala(fala: FalaPaciente):
    """Recebe a fala do paciente, processa e retorna a sugestão da IA."""
    if not agente.consulta_atual:
        return {"status": "erro", "mensagem": "Nenhuma consulta iniciada."}
    
    agente.processar_interacao(fala.texto)
    sugestao = agente.consulta_atual.sugestao_ia
    return {"status": "sucesso", "sugestao": sugestao}

@app.post("/consulta/finalizar", tags=["Consulta"])
def finalizar_consulta(decisao: DecisaoFinal):
    """Finaliza a consulta, registrando a decisão do médico."""
    if not agente.consulta_atual:
        return {"status": "erro", "mensagem": "Nenhuma consulta para finalizar."}
        
    agente.finalizar_consulta(decisao.decisao, decisao.resumo)
    gerenciador.salvar_medicos()
    return {"status": "sucesso", "mensagem": "Consulta finalizada e aprendizado registrado."}

@app.get("/relatorio", tags=["Análise"])
def obter_relatorio():
    """Gera e retorna o relatório reflexivo com base na memória."""
    relatorio = agente.executar_analise_de_sessao(obter_resposta_llm_api)
    return {"status": "sucesso", "relatorio": relatorio}