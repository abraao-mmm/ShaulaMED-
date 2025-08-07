# clinical_inference_real.py (Versão com Estruturação Clínica Completa)

import json
from typing import Callable

class RealInferenceEngine:
    """
    Usa uma LLM real para analisar a transcrição da consulta, estruturando-a
    em um formato de nota clínica completa (SOAP/anamnese).
    """
    def __init__(self, obter_resposta_llm_func: Callable):
        print("Motor de Inferência Clínica (ESTRUTURADO) inicializado.")
        self.obter_resposta_llm = obter_resposta_llm_func

    def _gerar_prompt_de_estruturacao(self, texto_consulta: str) -> str:
        # Novo schema JSON que reflete a estrutura de uma nota clínica
        schema_json = {
            "queixa_principal": "string",
            "historia_doenca_atual": "string",
            "antecedentes_pessoais_familiares": "string",
            "medicamentos_em_uso": "string",
            "exame_fisico_verbalizado": "string",
            "hipoteses_diagnosticas": ["string"],
            "conduta_sugerida": "string",
            "orientacoes_gerais": "string",
            "retorno_encaminhamento": "string"
        }

        prompt = (
            "Você é um assistente médico de IA altamente treinado, especialista em documentação clínica. Sua tarefa é ouvir a transcrição de uma consulta e organizá-la de forma estruturada, como uma nota de evolução de prontuário.\n\n"
            f"**TRANSCRIÇÃO COMPLETA DA CONSULTA:**\n\"{texto_consulta}\"\n\n"
            "**TAREFA:**\n"
            "Analise a transcrição e extraia as informações para cada uma das seções clínicas abaixo. Se uma informação para uma seção específica não for mencionada na transcrição, deixe o campo como uma string vazia (\"\").\n\n"
            "1.  **Queixa Principal:** O motivo principal da consulta, de forma concisa.\n"
            "2.  **História da Doença Atual (HDA):** Detalhamento da queixa, incluindo início, duração, características, fatores de melhora/piora.\n"
            "3.  **Antecedentes:** Histórico médico pessoal, familiar, cirurgias prévias, alergias, etc.\n"
            "4.  **Medicamentos em Uso:** Liste os medicamentos que o paciente já utiliza.\n"
            "5.  **Exame Físico:** Descreva os achados do exame físico que foram verbalizados pelo médico durante a consulta.\n"
            "6.  **Hipóteses Diagnósticas:** Liste as hipóteses que o médico considerou ou que podem ser inferidas dos dados.\n"
            "7.  **Conduta:** Descreva o plano de ação, incluindo exames solicitados e tratamentos prescritos.\n"
            "8.  **Orientações:** Conselhos e informações dadas ao paciente.\n"
            "9.  **Retorno/Encaminhamento:** Instruções sobre a próxima consulta ou encaminhamento para outro especialista.\n\n"
            f"Responda OBRIGATORIAMENTE em um formato JSON que siga este schema: {json.dumps(schema_json)}"
        )
        return prompt

    def gerar_nota_clinica_estruturada(self, texto_consulta: str) -> dict:
        if not texto_consulta:
            return {}

        prompt = self._gerar_prompt_de_estruturacao(texto_consulta)
        # O modo foi renomeado para refletir a nova tarefa
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