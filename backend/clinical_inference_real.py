# clinical_inference_real.py (Versão com Categorização e Análise de Estilo)

import json
from typing import Callable

class RealInferenceEngine:
    """
    Usa uma LLM real para analisar a transcrição da consulta e gerar
    hipóteses, sugestões, categorias e análise de estilo.
    """
    def __init__(self, obter_resposta_llm_func: Callable):
        print("Motor de Inferência Clínica (REAL, com IA Avançada) inicializado.")
        self.obter_resposta_llm = obter_resposta_llm_func

    def _gerar_prompt_hipoteses(self, texto_consulta: str) -> str:
        # Schema atualizado com os novos campos para as funcionalidades 10 e 11
        schema_json = {
            "hipoteses_diagnosticas": ["string"],
            "sugestao_conduta": "string",
            "exames_sugeridos": ["string"],
            "nivel_confianca_ia": "string (de 0.0 a 1.0)",
            "categoria_clinica": "string (ex: 'Gastrointestinal', 'Respiratório', 'Infeccioso', 'Ortopédico', 'Dermatológico', 'Neurológico', 'Cardiológico', 'Geral')",
            "nivel_intervencao_sugerido": "string ('Observacional', 'Conservador', 'Intervencionista')"
        }
        
        prompt = (
            "Você é um assistente médico de IA. Sua tarefa é analisar o relato de um paciente e fornecer uma análise clínica estruturada.\n\n"
            f"**RELATO DO PACIENTE:**\n\"{texto_consulta}\"\n\n"
            "**TAREFA:**\n"
            "1. Com base no relato, gere de 1 a 3 hipóteses diagnósticas, da mais provável para a menos provável.\n"
            "2. Sugira uma conduta clínica inicial ou um próximo passo investigativo.\n"
            "3. Liste exames que poderiam ajudar a confirmar o diagnóstico.\n"
            "4. Forneça um nível de confiança na sua análise principal (de 0.0 a 1.0).\n"
            "5. Categorize o caso numa única área clínica principal (ex: 'Gastrointestinal', 'Respiratório', 'Geral').\n"
            "6. Classifique o nível de intervenção da sua própria sugestão de conduta ('Observacional', 'Conservador', 'Intervencionista').\n\n"
            f"Responda OBRIGATORIAMENTE em um formato JSON que siga este schema: {json.dumps(schema_json)}"
        )
        return prompt

    def gerar_hipoteses_com_ia(self, texto_consulta: str) -> dict:
        if not texto_consulta:
            return {}

        prompt = self._gerar_prompt_hipoteses(texto_consulta)
        resposta_dict = self.obter_resposta_llm(prompt, modo="Diagnóstico Estruturado Avançado")
        
        conteudo = resposta_dict.get("conteudo", "{}")

        if isinstance(conteudo, dict):
            return conteudo
        
        if isinstance(conteudo, str):
            try:
                # Tenta limpar o JSON de possíveis blocos de markdown
                if "```json" in conteudo:
                    conteudo = conteudo.split("```json")[1].split("```")[0]
                
                return json.loads(conteudo)
            except json.JSONDecodeError:
                print("Erro: A IA não retornou um JSON válido para as hipóteses.")
                return {"erro": "Resposta da IA em formato inválido."}

        return {"erro": "Tipo de conteúdo inesperado recebido."}