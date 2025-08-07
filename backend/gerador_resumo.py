# gerador_resumo.py

import json
from typing import Callable, Dict

class GeradorDeResumo:
    """
    Especialista em pegar dados clínicos estruturados e gerar um resumo
    narrativo em formatos específicos (SOAP, etc.) para o prontuário.
    """
    def __init__(self, obter_resposta_llm_func: Callable):
        self.obter_resposta_llm = obter_resposta_llm_func

    def _criar_prompt_de_resumo(self, dados_clinicos: Dict, formato: str) -> str:
        # Converte o dicionário de dados em uma string formatada para o prompt
        dados_formatados = json.dumps(dados_clinicos, indent=2, ensure_ascii=False)

        prompt = (
            "Você é um assistente médico de IA, especialista em redigir notas de evolução para prontuários eletrônicos de forma clara e concisa.\n\n"
            "**TAREFA:**\n"
            f"Com base nos seguintes dados clínicos estruturados, gere uma nota evolutiva coesa e legível no formato **{formato.upper()}**. O texto deve ser corrido, profissional e pronto para ser copiado para um prontuário.\n\n"
            "**DADOS CLÍNICOS ESTRUTURADOS:**\n"
            f"{dados_formatados}\n\n"
            f"**NOTA EVOLUTIVA (FORMATO {formato.upper()}):**"
        )
        return prompt

    def gerar_resumo_para_prontuario(self, dados_clinicos: Dict, formato: str = "SOAP") -> str:
        """
        Orquestra a geração do resumo.

        Args:
            dados_clinicos: O dicionário com a nota clínica estruturada.
            formato: O formato desejado para o resumo (ex: "SOAP", "Livre").

        Returns:
            O texto do resumo gerado pela IA.
        """
        if not dados_clinicos:
            return "Não há dados suficientes para gerar um resumo."

        prompt = self._criar_prompt_de_resumo(dados_clinicos, formato)
        
        # Chama a IA com o prompt específico
        resposta_dict = self.obter_resposta_llm(prompt, modo=f"Geração de Resumo {formato}")
        
        resumo_gerado = resposta_dict.get("conteudo", "Não foi possível gerar o resumo.")
        
        return resumo_gerado