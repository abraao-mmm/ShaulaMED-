# refinador_de_prompt.py

import json
from typing import Callable

class RefinadorDePrompt:
    def __init__(self, obter_resposta_llm_func: Callable):
        self.obter_resposta_llm = obter_resposta_llm_func

    def _criar_prompt_de_analise(self, texto_bruto: str) -> str:
        prompt = (
            "Você é um especialista em linguística e contexto médico. A sua tarefa é analisar um texto transcrito de uma consulta, que pode conter erros, e melhorá-lo.\n\n"
            f"**TEXTO TRANSCRITO BRUTO:**\n\"{texto_bruto}\"\n\n"
            "**ANÁLISE E TAREFA:**\n"
            "1. Leia o texto e identifique se ele contém palavras incoerentes, erros gramaticais ou frases que não fazem sentido clínico (ex: 'caber vou me dar').\n"
            "2. Se o texto estiver incoerente, reescreva-o para a versão mais provável e clinicamente coerente, preservando o significado original.\n"
            "3. Se o texto já estiver perfeitamente claro e coerente, devolva-o exatamente como está.\n\n"
            "Responda OBRIGATORIAMENTE em um formato JSON com a seguinte estrutura: {\"texto_refinado\": \"o seu texto corrigido ou o original aqui\"}"
        )
        return prompt

    def refinar(self, texto_bruto: str) -> str:
        """
        Recebe um texto bruto, analisa a sua coerência e retorna uma versão refinada.
        """
        prompt = self._criar_prompt_de_analise(texto_bruto)
        
        # Chama a LLM para fazer a análise linguística
        resposta_dict = self.obter_resposta_llm(prompt, modo="Refinamento de Prompt")
        
        try:
            conteudo_str = resposta_dict.get("conteudo", "{}")
            conteudo_json = json.loads(conteudo_str)
            texto_refinado = conteudo_json.get("texto_refinado", texto_bruto)
            print(f"Texto Bruto: '{texto_bruto}' -> Texto Refinado: '{texto_refinado}'")
            return texto_refinado
        except (json.JSONDecodeError, AttributeError):
            # Se a IA falhar, devolvemos o texto original por segurança
            print("Refinador: A IA não retornou um JSON válido. Usando texto original.")
            return texto_bruto