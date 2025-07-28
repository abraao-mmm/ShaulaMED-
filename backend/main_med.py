# main_med.py (VERSÃO ATUALIZADA - Simula a arquitetura Stateless)

import openai
import json
from medico import Medico
from encontro_clinico import EncontroClinico
from shaulamed_agent import ShaulaMedAgent
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console
from rich.panel import Panel

# --- CONFIGURAÇÃO DA CONEXÃO COM A IA (LOCAL) ---
# Esta função conecta-se a um servidor de IA local para testes gratuitos.
# Altere a base_url se o seu servidor local (LM Studio, Ollama) usar uma porta diferente.
def obter_resposta_llm(prompt: str, modo: str = "Clínico") -> dict:
    """Função de conexão com a IA que será usada por todo o sistema."""
    console.print(f"\n[dim][Conectando à IA Local... Núcleo de '{modo}' ativado...][/dim]")
    
    # Garanta que você tem um modelo carregado no seu LM Studio ou Ollama
    MODELO_USADO = "lmstudio-community/Phi-3-mini-4k-instruct-GGUF" # Exemplo
    
    try:
        # Aponta para o servidor local
        client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        
        mensagens = [{"role": "user", "content": prompt}]
        
        # Adiciona instruções de formato JSON se necessário no prompt
        if "json" in prompt.lower():
             mensagens.insert(0, {"role": "system", "content": "Responda OBRIGATORIAMENTE em formato JSON."})

        response = client.chat.completions.create(
            model=MODELO_USADO,
            messages=mensagens,
            temperature=0.7,
        )
        conteudo = response.choices[0].message.content.strip()
        return {"tipo": "texto", "conteudo": conteudo}

    except Exception as e:
        console.print(f"❌ [bold red]Erro na chamada da IA Local: {e}[/bold red]")
        return {"tipo": "erro", "conteudo": "Erro ao conectar com a IA. Verifique se o LM Studio ou Ollama está rodando."}

# --- FUNÇÃO PRINCIPAL DA SIMULAÇÃO ---
def main():
    global console
    console = Console()
    console.clear()
    console.print(Panel.fit("[bold #00aaff]=== Simulador de Consultório - ShaulaMed v4.0 (Stateless Local Test) ===[/bold #00aaff]"))

    # --- INICIALIZAÇÃO ---
    # O gerenciador conecta-se ao Firebase real para carregar/salvar perfis.
    gerenciador = GerenciadorDeMedicos()
    
    # Para testes, usamos um ID fixo. O gerenciador irá carregar este perfil do Firestore
    # ou criar um novo se ele não existir.
    dados_utilizador_teste = {"localId": "TEST_UID_THALLES", "email": "thalles-teste@shaulamed.com"}
    medico_logado = gerenciador.carregar_ou_criar_perfil(dados_utilizador_teste)
    
    if not medico_logado:
        console.print("[bold red]Não foi possível carregar ou criar o perfil de teste. A sair.[/bold red]")
        return
        
    console.print(f"\n[green]Ambiente pronto para o(a) Dr(a). {medico_logado.apelido}.[/green]")
    
    # --- SIMULAÇÃO 1: CASO DE FARINGITE ---
    console.print("\n" + "-" * 60, style="dim")
    console.print("[bold yellow]INÍCIO DA CONSULTA 1[/bold yellow]")
    
    # 1. Iniciar (simula o front-end a chamar /consulta/iniciar)
    # O "estado" da consulta é guardado numa variável local, tal como no front-end.
    consulta_atual = EncontroClinico(medico_id=medico_logado.id, transcricao_consulta="")
    console.print(f"Objeto de consulta '{consulta_atual.id}' criado localmente.")

    # 2. Processar (simula o front-end a chamar /consulta/processar)
    # Para cada interação, um novo agente é instanciado na hora (lógica stateless).
    agente_processamento_1 = ShaulaMedAgent(medico=medico_logado, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm)
    agente_processamento_1.consulta_atual = consulta_atual # O estado é entregue ao agente
    agente_processamento_1.processar_interacao("Doutor, dor de garganta e febre há 2 dias.")
    
    # O estado atualizado é "devolvido" para a nossa variável local.
    consulta_atual = agente_processamento_1.consulta_atual
    console.print(Panel(json.dumps(consulta_atual.sugestao_ia, indent=2, ensure_ascii=False), title="[cyan]Sugestão da IA (em tempo real)[/cyan]"))

    # 3. Finalizar (simula o front-end a chamar /consulta/finalizar)
    decisao_medico_1 = "Realizado teste rápido para Strep (negativo). Prescrito Nimesulida."
    # Um novo agente é instanciado para o pedido de finalização.
    agente_finalizacao_1 = ShaulaMedAgent(medico=medico_logado, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm)
    agente_finalizacao_1.consulta_atual = consulta_atual # O estado final é entregue ao agente
    agente_finalizacao_1.finalizar_consulta(decisao_medico_1, "Resumo para o prontuário...")


    # --- SIMULAÇÃO 2: CASO DE DISPEPSIA ---
    console.print("\n" + "-" * 60, style="dim")
    console.print("[bold yellow]INÍCIO DA CONSULTA 2[/bold yellow]")
    
    # 1. Iniciar
    consulta_atual_2 = EncontroClinico(medico_id=medico_logado.id, transcricao_consulta="")
    console.print(f"Objeto de consulta '{consulta_atual_2.id}' criado localmente.")

    # 2. Processar
    agente_processamento_2 = ShaulaMedAgent(medico=medico_logado, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm)
    agente_processamento_2.consulta_atual = consulta_atual_2
    agente_processamento_2.processar_interacao("Sinto queimação no estômago e enjoo depois de comer.")
    consulta_atual_2 = agente_processamento_2.consulta_atual
    console.print(Panel(json.dumps(consulta_atual_2.sugestao_ia, indent=2, ensure_ascii=False), title="[cyan]Sugestão da IA (em tempo real)[/cyan]"))
    
    # 3. Finalizar
    decisao_medico_2 = "Solicitado teste respiratório para H. pylori e prescrito Omeprazol."
    agente_finalizacao_2 = ShaulaMedAgent(medico=medico_logado, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm)
    agente_finalizacao_2.consulta_atual = consulta_atual_2
    agente_finalizacao_2.finalizar_consulta(decisao_medico_2, "Resumo para o prontuário...")
    

    # --- GERAÇÃO DO RELATÓRIO PÓS-SESSÃO ---
    # Para gerar o relatório, instanciamos um agente final.
    # O seu construtor irá carregar do Firestore as duas consultas que acabámos de salvar.
    console.print("\n" + "-" * 60, style="dim")
    console.print("[bold magenta]A gerar relatório reflexivo da sessão...[/bold magenta]")
    agente_relatorio = ShaulaMedAgent(medico=medico_logado, gerenciador=gerenciador, console_log=console, obter_resposta_llm_func=obter_resposta_llm)
    
    # A memória do agente foi carregada do Firestore na sua criação
    relatorio_gerado = agente_relatorio.executar_analise_de_sessao(obter_resposta_llm)
    console.print(Panel(relatorio_gerado, title="[magenta]Painel Reflexivo (Gerado pela IA)[/magenta]", border_style="magenta"))
    
    console.print("\nSimulação concluída com sucesso.")

if __name__ == "__main__":
    main()