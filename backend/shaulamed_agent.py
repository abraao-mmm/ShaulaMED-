# shaulamed_agent.py (Versão Corrigida)

import json
from medico import Medico
from encontro_clinico import EncontroClinico
from clinical_inference_real import RealInferenceEngine
from memoria_clinica import MemoriaClinica
from analise_clinica import MotorDeAnaliseClinica
from refinador_de_prompt import RefinadorDePrompt
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console
from typing import Callable, Optional

class ShaulaMedAgent:
    def __init__(self, medico: Medico, gerenciador: GerenciadorDeMedicos, console_log: Console, obter_resposta_llm_func: Callable):
        self.medico = medico
        self.gerenciador = gerenciador
        self.console = console_log
        
        # Ao ser criado, o agente cria a memória, que por sua vez já carrega o histórico no seu __init__.
        self.memoria = MemoriaClinica(medico_id=self.medico.id)
        
        # A LINHA ABAIXO FOI REMOVIDA, pois era redundante e causava o erro.
        # self.memoria.carregar_encontros_do_medico(medico.id) <--- REMOVER
        
        self.inference_engine = RealInferenceEngine(obter_resposta_llm_func)
        self.motor_de_analise = MotorDeAnaliseClinica()
        self.refinador = RefinadorDePrompt(obter_resposta_llm_func)
        
        self.consulta_atual: Optional[EncontroClinico] = None

    def iniciar_nova_consulta(self):
        """Prepara o agente para uma nova consulta."""
        self.console.print(f"\n--- Iniciando nova consulta para Dr(a). {self.medico.apelido} ---")
        self.consulta_atual = EncontroClinico(medico_id=self.medico.id, transcricao_consulta="")

    def processar_interacao(self, transcricao_bruta: str):
        """Recebe a transcrição bruta, a refina, e depois gera hipóteses."""
        if self.consulta_atual:
            self.console.print(f"Processando transcrição: '{transcricao_bruta[:70]}...'")
            texto_refinado = self.refinador.refinar(transcricao_bruta)
            self.consulta_atual.transcricao_consulta = texto_refinado
            sugestao = self.inference_engine.gerar_hipoteses_com_ia(texto_refinado)
            self.consulta_atual.sugestao_ia = sugestao
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta foi iniciada.[/bold red]")

    def finalizar_consulta(self, decisao_medico_final: str, resumo_prontuario: str):
        """Finaliza a consulta e regista o aprendizado no Firestore."""
        if self.consulta_atual:
            self.console.print("--- Finalizando consulta e aprendendo ---")
            self.consulta_atual.decisao_medico_final = decisao_medico_final
            self.consulta_atual.texto_gerado_prontuario = resumo_prontuario
            hipoteses = self.consulta_atual.sugestao_ia.get("hipoteses_diagnosticas", [])
            if hipoteses:
                self.medico.aprender_com_conduta(hipoteses[0], decisao_medico_final)
                # Salva o perfil do médico atualizado no Firestore
                self.gerenciador.salvar_medico(self.medico)

            self.memoria.registrar_encontro(self.consulta_atual)
            self.consulta_atual = None
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta ativa para finalizar.[/bold red]")

    # Em shaulamed_agent.py

    def gerar_reflexao_pos_consulta(self, encontro: EncontroClinico, obter_resposta_llm_func: Callable) -> str:
        """Analisa um único encontro clínico e gera uma reflexão curta e perspicaz."""
        if not encontro: return "Não foi possível gerar a reflexão."
        
        # Mantemos os dados de entrada
        sugestao_ia_str = json.dumps(encontro.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"]))
        decisao_medico = encontro.decisao_medico_final
        
        # --- PROMPT ATUALIZADO ---
        # Instruções muito mais diretas para um estilo conciso e sereno.
        prompt = (
            "Você é a Shaula, uma IA serena e perspicaz que atua como copiloto de um médico. "
            "Sua tarefa é gerar um pensamento curto (um 'fun fact' clínico ou uma observação interessante) sobre a consulta que acabou de terminar, para ser exibido na tela inicial. "
            "Seja muito breve, como um pensamento passageiro de um colega.\n\n"
            f"**Decisão do Médico:** \"{decisao_medico}\"\n"
            f"**Suas Hipóteses Iniciais:** {sugestao_ia_str}\n\n"
            "**Sua Reflexão (máximo 2 frases, em tom de insight):**"
        )
        
        resposta_dict = obter_resposta_llm_func(prompt, modo="Reflexão Pós-Consulta")
        return resposta_dict.get("conteudo", "Consulta finalizada com sucesso.")

    def executar_analise_de_sessao(self, obter_resposta_llm_func: Callable) -> str:
        """Gera o relatório reflexivo da sessão com base nas consultas em memória."""
        self.console.print("\n[bold magenta]Gerando Relatório Reflexivo da Sessão...[/bold magenta]")
        return self.motor_de_analise.gerar_relatorio_semanal(
            encontros=self.memoria.encontros_em_memoria,
            nome_medico=self.medico.apelido,
            obter_resposta_llm_func=obter_resposta_llm_func
        )
        
    def gerar_despedida_do_dia(self, obter_resposta_llm_func: Callable) -> str:
        """Analisa as consultas do dia e gera uma mensagem de despedida personalizada."""
        consultas_do_dia = self.memoria.encontros_em_memoria 
        if not consultas_do_dia:
            return "Nenhuma consulta registada hoje. Tenha um bom descanso."
        temas = ", ".join(list(set([enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0] for enc in consultas_do_dia])))
        prompt = f"Você é a Shaula. O dia de trabalho do Dr(a). {self.medico.apelido} terminou. Hoje, ele(a) atendeu casos sobre: {temas}. Crie uma mensagem de despedida curta e serena."
        resposta_dict = obter_resposta_llm_func(prompt, modo="Despedida Reflexiva")
        return resposta_dict.get("conteudo", "Bom trabalho hoje. Tenha um bom descanso.")

    def salvar_memoria(self):
        # Este método torna-se menos relevante com o Firestore, mas pode ser mantido para backups locais se desejado.
        pass