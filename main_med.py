# main_med.py

import openai
import json
from medico import Medico
from shaulamed_agent import ShaulaMedAgent # Importa a versão mais recente do agente
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console
from rich.panel import Panel

# A função de conexão com a IA que será usada por todo o sistema
def obter_resposta_llm(prompt: str, modo: str = "Clínico", stream: bool = False, schema: dict = None) -> dict:
    console.print(f"\n[dim][Conectando à IA... Núcleo de '{modo}' ativado...][/dim]")
    # Garanta que você tem um modelo carregado no seu LM Studio
    MODELO_USADO = "lmstudio-community/Phi-3.1-mini-128k-instruct-GGUF"
    
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
        console.print(f"❌ [bold red]Erro na chamada da API da IA: {e}[/bold red]")
        return {"tipo": "erro", "conteudo": "Erro ao conectar com a IA. Verifique se o LM Studio está rodando."}


def main():
    # A variável console precisa ser acessível globalmente pela função obter_resposta_llm
    global console 
    console = Console()
    console.clear()
    console.print(Panel.fit("[bold #00aaff]=== Simulador de Consultório - ShaulaMed v0.5 (100% IA) ===[/bold #00aaff]"))

    # O gerenciador carrega ou cria o perfil do médico
    gerenciador = GerenciadorDeMedicos()
    medico_logado = gerenciador.definir_medico_atual(
        nome_medico="Thalles Rodrigues",
        crm="12345-AM",
        especialidade="Otorrinolaringologia"
    )
    
    # O agente é criado para o médico logado, passando a função de conexão com a IA
    agente = ShaulaMedAgent(
        medico=medico_logado, 
        console_log=console, 
        obter_resposta_llm_func=obter_resposta_llm
    )
    
    console.print(f"\n[green]Ambiente pronto para o(a) Dr(a). {agente.medico.nome}.[/green]")
    
    # --- SIMULAÇÃO 1: CASO DE FARINGITE ---
    console.print("\n" + "-" * 60, style="dim")
    console.print("[bold yellow]INÍCIO DA CONSULTA 1[/bold yellow]")
    agente.iniciar_nova_consulta()
    agente.processar_interacao("Doutor, dor de garganta e febre há 2 dias.")
    console.print(Panel(json.dumps(agente.consulta_atual.sugestao_ia, indent=2, ensure_ascii=False), title="[cyan]Sugestão da IA (em tempo real)[/cyan]"))
    decisao_medico_1 = "Realizado teste rápido para Strep (negativo). Prescrito Nimesulida."
    agente.finalizar_consulta(decisao_medico_1, "...")

    # --- SIMULAÇÃO 2: CASO DE DISPEPSIA ---
    console.print("\n" + "-" * 60, style="dim")
    console.print("[bold yellow]INÍCIO DA CONSULTA 2[/bold yellow]")
    agente.iniciar_nova_consulta()
    agente.processar_interacao("Sinto queimação no estômago e enjoo.")
    console.print(Panel(json.dumps(agente.consulta_atual.sugestao_ia, indent=2, ensure_ascii=False), title="[cyan]Sugestão da IA (em tempo real)[/cyan]"))
    decisao_medico_2 = "Solicitado teste respiratório para H. pylori."
    agente.finalizar_consulta(decisao_medico_2, "...")
    
    # --- GERAÇÃO DO RELATÓRIO ---
    console.print("\n" + "-" * 60, style="dim")
    relatorio_real = agente.executar_analise_de_sessao(obter_resposta_llm)
    console.print(Panel(relatorio_real, title="[magenta]Painel Reflexivo (Gerado pela IA)[/magenta]", border_style="magenta"))
    
    # Salva os perfis dos médicos (com o aprendizado da sessão)
    gerenciador.salvar_medicos()
    agente.salvar_memoria()
    console.print("\nSimulação concluída.")

if __name__ == "__main__":
    main()