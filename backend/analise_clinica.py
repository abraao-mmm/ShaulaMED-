# analise_clinica.py
from typing import List, Callable
from collections import Counter
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica inicializado.")

    def _criar_resumo_dos_encontros(self, encontros: List[EncontroClinico]) -> str:
        resumo_texto = []
        for enc in encontros:
            primeira_hipotese = enc.sugestao_ia.get("hipoteses", ["N/A"])[0]
            decisao = enc.decisao_medico_final
            discrepancia = "NÃO"
            if primeira_hipotese.lower() not in decisao.lower():
                 discrepancia = f"SIM (IA sugeriu '{primeira_hipotese}')"
            linha_resumo = (
                f"- Caso (Hipótese: {primeira_hipotese}): Decisão: '{decisao}'. Discrepância? {discrepancia}"
            )
            resumo_texto.append(linha_resumo)
        return "\n".join(resumo_texto)

    def _gerar_prompt_relatorio_clinico(self, resumo_clinico: str, nome_medico: str) -> str:
        prompt = (
            f"Você é um assistente de IA sênior analisando a prática clínica recente do(a) Dr(a). {nome_medico} para gerar um relatório reflexivo.\n\n"
            f"### RESUMO DAS CONSULTAS RECENTES:\n{resumo_clinico}\n\n"
            "### TAREFA: GERE UM RELATÓRIO REFLEXIVO ESTRUTURADO EM 5 PONTOS:\n\n"
            "**1. Resumo da Atividade:** Qual foi o volume de atendimentos e quais os temas clínicos mais comuns?\n\n"
            "**2. Padrões de Conduta:** Você consegue identificar algum padrão de tratamento do médico?\n\n"
"3. Análise de Concordância (IA vs. Médico): Para **CADA** caso listado, compare explicitamente a 'Hipótese Principal' da IA com a 'Decisão do Médico'. Aponte se elas **concordam ou divergem**. Se divergirem, analise o motivo da divergência (ex: resultado de exame, preferência do médico, etc.)."            "**4. Insight Destaque:** Aponte um insight interessante da semana.\n\n"
            "**5. Oportunidade de Reflexão:** Aponte uma área para reflexão de forma construtiva."
        )
        return prompt

    def gerar_relatorio_semanal(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> str:
        if not encontros:
            return "Nenhuma consulta registrada para análise."
        resumo = self._criar_resumo_dos_encontros(encontros)
        prompt_final = self._gerar_prompt_relatorio_clinico(resumo, nome_medico)
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Relatório Clínico")
        return resposta_dict.get("conteudo", "Não foi possível gerar o relatório.")