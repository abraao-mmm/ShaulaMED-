# shaulamed_agent.py

import json
from medico import Medico
from encontro_clinico import EncontroClinico
from clinical_inference_real import RealInferenceEngine
from memoria_clinica import MemoriaClinica
from analise_clinica import MotorDeAnaliseClinica
from refinador_de_prompt import RefinadorDePrompt
from gerenciador_medicos import GerenciadorDeMedicos
from rich.console import Console
from gerador_resumo import GeradorDeResumo
from analisador_clinico_avancado import AnalisadorClinicoAvancado
from typing import Callable, Optional

class ShaulaMedAgent:
    def __init__(self, medico: Medico, gerenciador: GerenciadorDeMedicos, console_log: Console, obter_resposta_llm_func: Callable):
        self.medico = medico
        self.gerenciador = gerenciador
        self.console = console_log
        
        self.memoria = MemoriaClinica(medico_id=self.medico.id)
        
        self.inference_engine = RealInferenceEngine(obter_resposta_llm_func)
        self.motor_de_analise = MotorDeAnaliseClinica()
        self.refinador = RefinadorDePrompt(obter_resposta_llm_func)
        self.gerador_de_resumo = GeradorDeResumo(obter_resposta_llm_func)
        self.analisador_avancado = AnalisadorClinicoAvancado(obter_resposta_llm_func)
        
        self.consulta_atual: Optional[EncontroClinico] = None

    def processar_interacao(self, transcricao_bruta: str):
        """
        Recebe a transcrição, a refina, estrutura a nota e, em seguida,
        executa a análise clínica avançada sobre ela.
        """
        if self.consulta_atual:
            self.console.print(f"Processando transcrição: '{transcricao_bruta[:70]}...'")
            texto_refinado = self.refinador.refinar(transcricao_bruta)
            self.consulta_atual.transcricao_consulta = texto_refinado
            
            # Etapa 1: Estruturar a nota clínica
            nota_estruturada = self.inference_engine.gerar_nota_clinica_estruturada(texto_refinado)
            
            # Etapa 2: Executar a análise avançada sobre a nota estruturada
            analise_avancada = self.analisador_avancado.executar_analise_avancada(nota_estruturada)

            # Combina os dois resultados em um único objeto para o frontend
            self.consulta_atual.sugestao_ia = {
                "nota_clinica_estruturada": nota_estruturada,
                "analise_clinica_avancada": analise_avancada
            }
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta foi iniciada.[/bold red]")

    def finalizar_consulta(self, decisao_medico_final: str, obter_resposta_llm_func: Callable, formato_resumo: str = "SOAP") -> dict:
        """
        Finaliza a consulta, gera o resumo e a reflexão, e retorna ambos
        num dicionário.
        """
        if self.consulta_atual:
            self.console.print(f"--- Finalizando consulta e gerando resumo ({formato_resumo}) ---")
            self.consulta_atual.decisao_medico_final = decisao_medico_final
            
            # Gera o resumo para o prontuário
            dados_para_resumo = self.consulta_atual.sugestao_ia.get("nota_clinica_estruturada", {})
            resumo_gerado = self.gerador_de_resumo.gerar_resumo_para_prontuario(dados_para_resumo, formato_resumo)
            self.consulta_atual.texto_gerado_prontuario = resumo_gerado
            
            # Gera a reflexão curta sobre a consulta
            reflexao = self.gerar_reflexao_pos_consulta(self.consulta_atual, obter_resposta_llm_func)
            self.consulta_atual.reflexao_ia = reflexao # Salva a reflexão no objeto
            
            # Aprende e salva no banco de dados
            hipoteses = self.consulta_atual.sugestao_ia.get("nota_clinica_estruturada", {}).get("hipoteses_diagnosticas", [])
            if hipoteses:
                self.medico.aprender_com_conduta(hipoteses[0], decisao_medico_final)
                self.gerenciador.salvar_medico(self.medico)

            self.memoria.registrar_encontro(self.consulta_atual)
            self.consulta_atual = None # Limpa a consulta atual

            # RETORNA UM DICIONÁRIO COM AMBOS OS RESULTADOS
            return {
                "texto_gerado_prontuario": resumo_gerado,
                "reflexao": reflexao
            }
        else:
            self.console.print("[bold red]Erro: Nenhuma consulta ativa para finalizar.[/bold red]")
            return {
                "texto_gerado_prontuario": "Erro: Nenhuma consulta para finalizar.",
                "reflexao": "Ocorreu um erro."
            }

    def gerar_reflexao_pos_consulta(self, encontro: EncontroClinico, obter_resposta_llm_func: Callable) -> str:
        """Analisa um único encontro clínico e gera uma reflexão curta e perspicaz, com foco em um fun fact."""
        if not encontro: return "Não foi possível gerar a reflexão."
        
        dados_anamnese = encontro.sugestao_ia.get("nota_clinica_estruturada", {})
        
        prompt = (
            "Você é a Shaula, uma IA serena e perspicaz que atua como copiloto de um médico. "
            "Sua tarefa é gerar uma curiosidade ou um 'fun fact' clínico interessante sobre a consulta que acabou de terminar, para ser exibido na tela inicial. "
            "Seja muito breve (uma ou duas frases) e foque em algo educativo ou que estimule a reflexão, evitando apenas repetir o diagnóstico.\n\n"
            f"**Dados da Anamnese:**\n"
            f"- Queixa: {dados_anamnese.get('queixa_principal', 'Não informada')}\n"
            f"- HDA: {dados_anamnese.get('historia_doenca_atual', 'Não informada')}\n"
            f"**Suas Hipóteses Iniciais:** {dados_anamnese.get('hipoteses_diagnosticas', [])}\n\n"
            "**Sua Reflexão (em tom de insight ou curiosidade):**"
        )
        
        resposta_dict = obter_resposta_llm_func(prompt, modo="Reflexão Pós-Consulta")
        return resposta_dict.get("conteudo", "Consulta finalizada com sucesso.")

    def executar_analise_de_sessao(self, obter_resposta_llm_func: Callable) -> str:
        """Gera o relatório reflexivo da sessão com base nas consultas em memória."""
        self.console.print("\n[bold magenta]Gerando Relatório Reflexivo da Sessão...[/bold magenta]")
        # Nota: A função no MotorDeAnaliseClinica foi renomeada para gerar_relatorio_semanal_completo
        relatorio_completo = self.motor_de_analise.gerar_relatorio_semanal_completo(
            encontros=self.memoria.encontros_em_memoria,
            nome_medico=self.medico.apelido,
            obter_resposta_llm_func=obter_resposta_llm_func
        )
        # Retornamos apenas a parte textual para compatibilidade ou o objeto completo se necessário
        return relatorio_completo.get("texto_coach", "Não foi possível gerar o relatório.")