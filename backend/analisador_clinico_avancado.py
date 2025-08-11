import json
from typing import Callable, Dict

class AnalisadorClinicoAvancado:
    def __init__(self, obter_resposta_llm_func: Callable):
        self.obter_resposta_llm = obter_resposta_llm_func

    def _criar_prompt_analise_avancada(self, dados_clinicos: Dict) -> str:
        dados_formatados = json.dumps(dados_clinicos, indent=2, ensure_ascii=False)
        
        schema_json_analise = {
            "exames_complementares_sugeridos": [{
                "exame": "string",
                "justificativa": "string (explique o raciocínio clínico para esta sugestão)"
            }],
            "sugestoes_de_tratamento": [{
                "medicamento_sugerido": "string (incluir classe do medicamento)",
                "posologia_recomendada": "string (dose, via, frequência e duração)",
                "justificativa_clinica": "string (explique por que este tratamento é apropriado com base nas hipóteses e diretrizes atuais)"
            }]
        }

        prompt = (
            "Você é uma IA de apoio à decisão clínica, agindo como um consultor especialista. Sua análise deve ser baseada em evidências e diretrizes médicas atualizadas. Analise a nota clínica estruturada e forneça insights acionáveis e bem fundamentados.\n\n"
            f"**NOTA CLÍNICA PARA ANÁLISE:**\n{dados_formatados}\n\n"
            "**TAREFAS DE ANÁLISE AVANÇADA:**\n"
            "1.  **Sugerir Exames Complementares:** Com base nas hipóteses, sugira exames cruciais, justificando cada um com o raciocínio clínico (ex: 'Solicitar Exame X para descartar a Hipótese Y, dado o sintoma Z').\n"
            "2.  **Sugerir Tratamentos:** Com base nas hipóteses mais prováveis, sugira um plano terapêutico. Para cada medicamento, forneça a posologia completa e uma justificativa clara para a sua escolha (ex: 'Iniciar com Droga A, que é a primeira linha segundo a diretriz B para a condição C').\n\n"
            "Se não houver nada a acrescentar para uma determinada seção, retorne uma lista vazia `[]` para ela.\n"
            f"Responda OBRIGATORIAMENTE em um formato JSON que siga este schema: {json.dumps(schema_json_analise)}"
        )
        return prompt

    def executar_analise_avancada(self, dados_clinicos: Dict) -> Dict:
        # ... (o resto da função permanece o mesmo)
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