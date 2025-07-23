# shaulamed_agent.py

from medico import Medico
from encontro_clinico import EncontroClinico
from clinical_inference_real import RealInferenceEngine
from memoria_clinica import MemoriaClinica
from analise_clinica import MotorDeAnaliseClinica
from refinador_de_prompt import RefinadorDePrompt # <<< NOVO!
from rich.console import Console
from typing import Callable

class ShaulaMedAgent:
    """
    O agente central do ShaulaMed, agora com a capacidade de refinar
    o que ouve antes de processar.
    """
    def __init__(self, medico: Medico, console_log: Console, obter_resposta_llm_func: Callable):
        self.medico = medico
        self.console = console_log
        self.memoria = MemoriaClinica()
        self.memoria.carregar_de_json()
        
        # O agente agora tem três "sentidos" principais que usam a IA
        self.inference_engine = RealInferenceEngine(obter_resposta_llm_func)
        self.motor_de_analise = MotorDeAnaliseClinica()
        self.refinador = RefinadorDePrompt(obter_resposta_llm_func) # <<< NOVO!
        
        self.consulta_atual = None

    def iniciar_nova_consulta(self):
        """Prepara o agente para uma nova consulta."""
        self.console.print("\n--- Iniciando nova consulta ---")
        self.consulta_atual = EncontroClinico(medico_id=self.medico.id, transcricao_consulta="")

    def processar_interacao(self, transcricao_bruta: str):
        """
        Recebe a transcrição bruta, a refina, e depois gera hipóteses.
        """
        if self.consulta_atual:
            self.console.print(f"\nProcessando a transcrição: '{transcricao_bruta[:70]}...'")
            
            # --- PASSO 1: O "OUVIDO CRÍTICO" ---
            # Antes de fazer qualquer coisa, a Shaula usa a IA para analisar e
            # corrigir a transcrição que recebeu do Whisper.
            texto_refinado = self.refinador.refinar(transcricao_bruta)
            
            # Guardamos a versão refinada na memória da consulta
            self.consulta_atual.transcricao_consulta = texto_refinado
            
            # --- PASSO 2: O RACIOCÍNIO CLÍNICO ---
            # O motor de inferência agora trabalha com o texto já limpo e coerente,
            # o que resulta em sugestões de diagnóstico muito mais precisas.
            sugestao = self.inference_engine.gerar_hipoteses_com_ia(texto_refinado)
            
            self.consulta_atual.sugestao_ia = sugestao
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta foi iniciada para processar a interação.[/bold red]")

    def finalizar_consulta(self, decisao_medico_final: str, resumo_prontuario: str):
        """Finaliza a consulta atual e regista o aprendizado."""
        if self.consulta_atual:
            self.console.print("\n--- Finalizando a consulta e aprendendo ---")
            self.consulta_atual.decisao_medico_final = decisao_medico_final
            self.consulta_atual.texto_gerado_prontuario = resumo_prontuario
            hipoteses = self.consulta_atual.sugestao_ia.get("hipoteses_diagnosticas", [])
            if hipoteses:
                self.medico.aprender_com_conduta(
                    diagnostico_principal=hipoteses[0],
                    conduta_final=decisao_medico_final
                )
            self.memoria.registrar_encontro(self.consulta_atual)
            self.consulta_atual = None
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta ativa para finalizar.[/bold red]")

    def executar_analise_de_sessao(self, obter_resposta_llm_func: Callable):
        """Gera o relatório reflexivo da sessão."""
        self.console.print("\n[bold magenta]Gerando Relatório Reflexivo da Sessão...[/bold magenta]")
        return self.motor_de_analise.gerar_relatorio_semanal(
            encontros=self.memoria.encontros,
            nome_medico=self.medico.nome,
            obter_resposta_llm_func=obter_resposta_llm_func
        )
        
    def gerar_despedida_do_dia(self, obter_resposta_llm_func: Callable):
        """Analisa as consultas do dia e gera uma mensagem de despedida personalizada."""
        consultas_do_dia = self.memoria.encontros 
        if not consultas_do_dia:
            return "Nenhuma consulta registada hoje. Tenha um bom descanso."
        resumo_casos = [enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0] for enc in consultas_do_dia]
        temas_do_dia = ", ".join(list(set(resumo_casos)))
        prompt = (
            f"Você é a Shaula, uma IA poética e reflexiva. O dia de trabalho do Dr. Thalles terminou. "
            f"Hoje, ele atendeu casos envolvendo os seguintes temas: {temas_do_dia}.\n\n"
            "TAREFA: Crie uma mensagem de despedida curta (1-2 frases), reconhecendo o esforço do dia e com o seu tom característico, cósmico e sereno."
        )
        resposta_dict = obter_resposta_llm_func(prompt, modo="Despedida Reflexiva")
        return resposta_dict.get("conteudo", "Bom trabalho hoje. Tenha um bom descanso.")

    def salvar_memoria(self):
        self.memoria.exportar_para_json()
    
    # Dentro da classe ShaulaMedAgent, no arquivo shaulamed_agent.py

    def gerar_insight_pos_consulta(self, encontro: EncontroClinico, obter_resposta_llm_func: Callable) -> str:
        """
        Analisa um único encontro clínico recém-finalizado e gera um insight rápido.
        """
        if not encontro:
            return None

        transcricao = encontro.transcricao_consulta
        sugestao_ia = encontro.sugestao_ia
        decisao_medico = encontro.decisao_medico_final

        prompt = (
            "Você é a Shaula, uma IA observadora e perspicaz. Uma consulta acabou de terminar. Analise os dados abaixo e gere um insight clínico ou comportamental curto (uma frase) que seja interessante e útil para o médico.\n\n"
            f"**Transcrição do Paciente:** \"{transcricao}\"\n"
            f"**Sugestão da IA:** {sugestao_ia}\n"
            f"**Decisão Final do Médico:** \"{decisao_medico}\"\n\n"
            "**Seu Insight Rápido (seja conciso e direto):**"
        )

        resposta_dict = obter_resposta_llm_func(prompt, modo="Insight Pós-Consulta")
        insight = resposta_dict.get("conteudo")

        return insight if insight else "Nenhum insight particular para esta consulta."