# clinical_inference_real.py
import json
from typing import Callable

class RealInferenceEngine:
    def __init__(self, obter_resposta_llm_func: Callable):
        print("Motor de Inferência Clínica (ESTRUTURADO AVANÇADO) inicializado.")
        self.obter_resposta_llm = obter_resposta_llm_func

    def _gerar_prompt_de_estruturacao(self, texto_consulta: str) -> str:
        
        # ===== MUDANÇA PRINCIPAL AQUI =====
        # Mudamos o schema para quebrar a anamnese em campos curtos e diretos.
        schema_json = {
            "queixa_principal": "string (resumo conciso em jargão médico, ex: 'Epigastralgia pós-prandial')",
            "anamnese": {
                "sintoma_principal": "string (O sintoma principal, ex: 'Dor de garganta')",
                "inicio_e_duracao": "string (ex: 'Há 2 dias')",
                "sintomas_associados": "string (ex: 'Febre, tosse seca')",
                "fatores_melhora_piora": "string (ex: 'Piora ao deitar')",
            },
            "antecedentes_pessoais_familiares": "string (histórico médico relevante, comorbidades, cirurgias, alergias, histórico familiar)",
            "medicamentos_em_uso": "string (listar medicamentos, doses e frequência, se mencionado)",
            "exame_fisico_verbalizado": "string (descrever achados objetivos do exame físico mencionados pelo médico)",
            "hipoteses_diagnosticas": ["string (listar pelo menos 3 hipóteses em ordem de probabilidade, usando termos técnicos)"],
        }
        # ==================================

        prompt = (
            "Você é um assistente de IA especialista em documentação médica para um médico experiente. Sua tarefa é ouvir a transcrição de uma consulta e estruturá-la de forma técnica, precisa e detalhada, como se fosse para um prontuário de alto nível.\n\n"
            f"**TRANSCRIÇÃO DA CONSULTA:**\n\"{texto_consulta}\"\n\n"
            "**TAREFA:**\n"
            "Analise a transcrição e extraia as informações, preenchendo cada campo do schema JSON abaixo com o máximo de detalhe e precisão técnica possível. Seja conciso e direto nos campos da 'anamnese'. Se uma informação não for mencionada, deixe o campo como uma string vazia (\"\").\n\n"
            f"Responda OBRIGATORIAMENTE em formato JSON, seguindo este schema: {json.dumps(schema_json)}"
        )
        return prompt

    def gerar_nota_clinica_estruturada(self, texto_consulta: str) -> dict:
        if not texto_consulta:
            return {}
        prompt = self._gerar_prompt_de_estruturacao(texto_consulta)
        resposta_dict = self.obter_resposta_llm(prompt, modo="Estruturação de Nota Clínica")
        conteudo = resposta_dict.get("conteudo", "{}")
        if isinstance(conteudo, dict):
            return conteudo
        if isinstance(conteudo, str):
            try:
                if "```json" in conteudo:
                    conteudo = conteudo.split("```json")[1].split("```")[0]
                return json.loads(conteudo)
            except json.JSONDecodeError:
                print("Erro: A IA não retornou um JSON válido para a nota clínica.")
                return {"erro": "Resposta da IA em formato inválido."}
        return {"erro": "Tipo de conteúdo inesperado recebido."}