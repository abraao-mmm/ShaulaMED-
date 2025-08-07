# analisador_clinico_avancado.py

import json
from typing import Callable, Dict

class AnalisadorClinicoAvancado:
    """
    Realiza uma análise clínica aprofundada sobre uma nota já estruturada,
    atuando como um sistema de apoio à decisão clínica.
    """
    def __init__(self, obter_resposta_llm_func: Callable):
        self.obter_resposta_llm = obter_resposta_llm_func

    def _criar_prompt_analise_avancada(self, dados_clinicos: Dict) -> str:
        dados_formatados = json.dumps(dados_clinicos, indent=2, ensure_ascii=False)
        
        # Schema para a resposta JSON da análise avançada
        schema_json_analise = {
            "exames_complementares_sugeridos": [{
                "exame": "string",
                "justificativa": "string"
            }],
            "alertas_de_conduta": [{
                "alerta": "string",
                "explicacao_risco": "string"
            }],
            "sugestoes_de_tratamento": [{
                "medicamento_sugerido": "string",
                "posologia_recomendada": "string",
                "justificativa_clinica": "string"
            }],
            "validacao_medicamentos_mencionados": [{
                "medicamento_mencionado": "string",
                "status_validacao": "string (ex: Aprovado, Alerta de Interação, Dose Incomum)",
                "observacao": "string"
            }]
        }

        prompt = (
            "Você é uma IA de apoio à decisão clínica, baseada em evidências científicas atualizadas. Sua tarefa é analisar uma nota clínica estruturada e fornecer insights críticos e sugestões.\n\n"
            f"**NOTA CLÍNICA ESTRUTURADA PARA ANÁLISE:**\n{dados_formatados}\n\n"
            "**TAREFAS DE ANÁLISE AVANÇADA:**\n"
            "1.  **Sugerir Exames Complementares:** Com base nas hipóteses, sugira exames relevantes que não foram mencionados, explicando o porquê de cada um.\n"
            "2.  **Alertar sobre Condutas:** Identifique qualquer parte da conduta ou prescrição que possa ser não recomendada (ex: contraindicação, tratamento desatualizado) e explique o risco.\n"
            "3.  **Sugerir Tratamentos:** Com base no perfil do paciente (idade, sintomas) e nas hipóteses, sugira tratamentos específicos, incluindo posologia e a justificativa.\n"
            "4.  **Validar Medicamentos:** Analise os medicamentos já em uso ou prescritos quanto a interações medicamentosas potenciais, doses para a faixa etária/peso (se disponível) e adequação geral.\n\n"
            "Se não houver nada a acrescentar para uma determinada seção, retorne uma lista vazia `[]` para ela.\n"
            f"Responda OBRIGATORIAMIAMENTE em um formato JSON que siga este schema: {json.dumps(schema_json_analise)}"
        )
        return prompt

    def executar_analise_avancada(self, dados_clinicos: Dict) -> Dict:
        """
        Orquestra a chamada à IA para a análise avançada.
        """
        if not dados_clinicos or dados_clinicos.get("erro"):
            return {}

        prompt = self._criar_prompt_analise_avancada(dados_clinicos)
        resposta_dict = self.obter_resposta_llm(prompt, modo="Análise Clínica Avançada")
        conteudo = resposta_dict.get("conteudo", "{}")

        try:
            if "```json" in conteudo:
                conteudo = conteudo.split("```json")[1].split("```")[0]
            return json.loads(conteudo)
        except json.JSONDecodeError:
            print("Erro: A IA não retornou um JSON válido para a análise avançada.")
            return {"erro": "Resposta da IA em formato inválido."}