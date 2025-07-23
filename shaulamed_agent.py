# shaulamed_agent.py (CORRIGIDO)

from medico import Medico
from encontro_clinico import EncontroClinico
from clinical_inference_real import RealInferenceEngine
from memoria_clinica import MemoriaClinica
from analise_clinica import MotorDeAnaliseClinica
from rich.console import Console
from typing import Callable

class ShaulaMedAgent:
    def __init__(self, medico: Medico, console_log: Console, obter_resposta_llm_func: Callable):
        self.medico = medico
        self.console = console_log
        self.memoria = MemoriaClinica()
        self.memoria.carregar_de_json()
        self.inference_engine = RealInferenceEngine(obter_resposta_llm_func)
        self.motor_de_analise = MotorDeAnaliseClinica()
        self.consulta_atual = None

    # --- MÉTODO CORRIGIDO QUE ESTAVA FALTANDO ---
    def iniciar_nova_consulta(self):
        """Prepara o agente para uma nova consulta, criando um novo EncontroClinico."""
        self.console.print("\n--- Iniciando nova consulta ---")
        self.consulta_atual = EncontroClinico(medico_id=self.medico.id, transcricao_consulta="")

    def processar_interacao(self, transcricao_da_fala: str):
        if self.consulta_atual:
            self.console.print(f"\nProcessando a transcrição com IA: '{transcricao_da_fala[:70]}...'")
            self.consulta_atual.transcricao_consulta = transcricao_da_fala
            sugestao = self.inference_engine.gerar_hipoteses_com_ia(transcricao_da_fala)
            self.consulta_atual.sugestao_ia = sugestao
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta foi iniciada para processar a interação.[/bold red]")

    def finalizar_consulta(self, decisao_medico_final: str, resumo_prontuario: str):
        if self.consulta_atual:
            self.console.print("\n--- Finalizando a consulta e aprendendo ---")
            self.consulta_atual.decisao_medico_final = decisao_medico_final
            self.consulta_atual.texto_gerado_prontuario = resumo_prontuario
            hipoteses = self.consulta_atual.sugestao_ia.get("hipoteses", [])
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
        self.console.print("\n[bold magenta]Gerando Relatório Reflexivo da Sessão...[/bold magenta]")
        return self.motor_de_analise.gerar_relatorio_semanal(
            encontros=self.memoria.encontros,
            nome_medico=self.medico.nome,
            obter_resposta_llm_func=obter_resposta_llm_func
        )

    def salvar_memoria(self):
        self.memoria.exportar_para_json()