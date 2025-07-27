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
from typing import Callable, Optional

class ShaulaMedAgent:
    def __init__(self, medico: Medico, gerenciador: GerenciadorDeMedicos, console_log: Console, obter_resposta_llm_func: Callable):
        self.medico = medico
        self.gerenciador = gerenciador
        self.console = console_log
        self.memoria = MemoriaClinica()
        self.memoria.carregar_encontros_do_medico(medico.id)
        
        self.inference_engine = RealInferenceEngine(obter_resposta_llm_func)
        self.motor_de_analise = MotorDeAnaliseClinica()
        self.refinador = RefinadorDePrompt(obter_resposta_llm_func)
        
        self.consulta_atual: Optional[EncontroClinico] = None

    def iniciar_nova_consulta(self):
        self.console.print(f"\n--- Iniciando nova consulta para Dr(a). {self.medico.apelido} ---")
        self.consulta_atual = EncontroClinico(medico_id=self.medico.id, transcricao_consulta="")

    def processar_interacao(self, transcricao_bruta: str):
        if self.consulta_atual:
            texto_refinado = self.refinador.refinar(transcricao_bruta)
            self.consulta_atual.transcricao_consulta = texto_refinado
            sugestao = self.inference_engine.gerar_hipoteses_com_ia(texto_refinado)
            self.consulta_atual.sugestao_ia = sugestao

    def finalizar_consulta(self, decisao_medico_final: str, resumo_prontuario: str):
        if self.consulta_atual:
            self.consulta_atual.decisao_medico_final = decisao_medico_final
            self.consulta_atual.texto_gerado_prontuario = resumo_prontuario
            hipoteses = self.consulta_atual.sugestao_ia.get("hipoteses_diagnosticas", [])
            if hipoteses:
                self.medico.aprender_com_conduta(hipoteses[0], decisao_medico_final)
                self.gerenciador.salvar_medico(self.medico)
            self.memoria.registrar_encontro(self.consulta_atual)

    def gerar_reflexao_pos_consulta(self, encontro: EncontroClinico, obter_resposta_llm_func: Callable) -> str:
        if not encontro: return "Não foi possível gerar a reflexão."
        sugestao_ia_str = json.dumps(encontro.sugestao_ia)
        decisao_medico = encontro.decisao_medico_final
        prompt = (
            "Você é a Shaula. Analise a consulta e gere uma reflexão curta e perspicaz.\n\n"
            f"**Sua Sugestão:**\n{sugestao_ia_str}\n\n"
            f"**Decisão do Médico:**\n\"{decisao_medico}\"\n\n"
            "**Sua Reflexão:**"
        )
        resposta_dict = obter_resposta_llm_func(prompt, modo="Reflexão Pós-Consulta")
        return resposta_dict.get("conteudo", "Consulta finalizada.")