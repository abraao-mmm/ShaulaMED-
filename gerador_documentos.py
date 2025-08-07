# gerador_documentos.py

import json
from typing import Callable, Dict

class GeradorDeDocumentos:
    """
    Especialista em criar documentos clínicos formatados (receitas, atestados, etc.)
    a partir dos dados de uma consulta.
    """
    def __init__(self, obter_resposta_llm_func: Callable):
        self.obter_resposta_llm = obter_resposta_llm_func

    def _criar_prompt_documento(self, tipo_documento: str, dados_clinicos: str, dados_medico: str) -> str:
        
        exemplos_formato = {
            "receita": "RECEITUÁRIO MÉDICO\n\nPaciente: [Nome do Paciente, se disponível]\n\nUso Contínuo:\n1. [Medicamento] - [Dosagem]\n\n[Assinatura do Médico]\n[Nome Completo do Médico]\n[CRM]",
            "atestado": "ATESTADO MÉDICO\n\nAtesto, para os devidos fins, que o(a) Sr(a). [Nome do Paciente] necessita de [Número] dias de afastamento de suas atividades laborais a partir desta data, por motivos de doença (CID: [CID, se aplicável]).\n\n[Local, Data]\n\n[Assinatura do Médico]\n[Nome Completo do Médico]\n[CRM]",
            "encaminhamento": "ENCAMINHAMENTO MÉDICO\n\nEncaminho o(a) paciente [Nome do Paciente] para avaliação com especialista em [Especialidade], por apresentar quadro de [Diagnóstico/Sintomas].\n\nAtenciosamente,\n\n[Assinatura do Médico]\n[Nome Completo do Médico]\n[CRM]"
        }

        formato_exemplo = exemplos_formato.get(tipo_documento, "Formato padrão de documento médico.")

        prompt = (
            f"Você é um assistente administrativo médico. Sua tarefa é gerar um '{tipo_documento.replace('_', ' ').title()}' com base nas informações clínicas fornecidas. O documento deve ser formal e pronto para impressão.\n\n"
            f"**INFORMAÇÕES DO MÉDICO:**\n{dados_medico}\n\n"
            f"**DADOS CLÍNICOS DA CONSULTA:**\n{dados_clinicos}\n\n"
            f"**TAREFA:**\n"
            f"Gere o texto completo para o documento solicitado. Utilize as informações fornecidas e siga estritamente o formato e o tom de um documento médico oficial. Se alguma informação específica (como nome do paciente) não estiver nos dados, use um placeholder como '[Nome do Paciente]'.\n\n"
            f"**EXEMPLO DE FORMATAÇÃO ESPERADA:**\n{formato_exemplo}\n\n"
            f"**DOCUMENTO GERADO:**"
        )
        return prompt

    def gerar_documento(self, tipo_documento: str, dados_consulta: Dict, dados_medico: Dict) -> str:
        if not dados_consulta:
            return f"Não há dados suficientes da consulta para gerar o(a) {tipo_documento}."

        dados_clinicos_str = json.dumps(dados_consulta, indent=2, ensure_ascii=False)
        dados_medico_str = json.dumps(dados_medico, indent=2, ensure_ascii=False)

        prompt = self._criar_prompt_documento(tipo_documento, dados_clinicos_str, dados_medico_str)
        
        resposta_dict = self.obter_resposta_llm(prompt, modo=f"Geração de {tipo_documento}")
        
        documento_gerado = resposta_dict.get("conteudo", f"Não foi possível gerar o(a) {tipo_documento}.")
        
        return documento_gerado