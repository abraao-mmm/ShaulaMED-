# analise_clinica.py (Versão com Prompt de Coach Clínico)

from typing import List, Callable
from collections import Counter
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        # O print pode ser removido em produção se desejar
        print("Motor de Análise Clínica (Coach) inicializado.")

    def _criar_resumo_dos_encontros(self, encontros: List[EncontroClinico]) -> str:
        """Cria um resumo factual dos encontros para alimentar o prompt da IA."""
        resumo_texto = []
        for i, enc in enumerate(encontros):
            hipotese_ia = enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0]
            decisao_medico = enc.decisao_medico_final
            
            discrepancia = "Não"
            if hipotese_ia.lower() not in decisao_medico.lower():
                 discrepancia = f"Sim (IA sugeriu '{hipotese_ia}')"

            linha_resumo = (
                f"- Consulta {i+1}: Queixa principal levou à decisão '{decisao_medico}'. "
                f"Houve divergência com a sugestão da IA? {discrepancia}"
            )
            resumo_texto.append(linha_resumo)
        return "\n".join(resumo_texto)

    def _gerar_prompt_relatorio_clinico(self, resumo_clinico: str, nome_medico: str) -> str:
        """
        NOVO PROMPT: Instruções para a IA atuar como um coach clínico,
        usando um tom pessoal, insights comparativos e uma pergunta final.
        """
        prompt = (
            f"Você é a Shaula, uma IA que atua como uma coach clínica serena e perspicaz para o(a) Dr(a). {nome_medico}. "
            "Sua tarefa é gerar um 'Painel Semanal' que o ajude a refletir sobre sua prática recente. Use um tom pessoal e encorajador.\n\n"
            f"### DADOS BRUTOS DA SEMANA:\n{resumo_clinico}\n\n"
            "### ESTRUTURA DO SEU PAINEL (siga estes 4 pontos):\n\n"
            "**1. Olá, Dr(a). {nome_medico}! (Saudação Pessoal):** Comece com uma saudação calorosa e um resumo de 1 frase sobre a semana.\n\n"
            "**2. Seu Padrão de Destaque (Insight Comparativo):** Analise os casos da semana. Você notou algum padrão ou tema recorrente? Compare com o que você poderia considerar um 'padrão habitual' do médico. Exemplo: 'Notei que nesta semana você investigou mais causas infecciosas do que o habitual.' ou 'Sua abordagem pareceu mais conservadora esta semana, focando em tratamentos sintomáticos.'\n\n"
            "**3. Nosso Ponto de Calibração (Análise de Divergência):** Comente sobre os casos em que a decisão do médico foi diferente da sua sugestão inicial. Aborde isso de forma positiva. Exemplo: 'Tivemos alguns momentos de calibração esta semana, onde você seguiu um caminho diferente do que sugeri. Isso é ótimo, pois é assim que aprendo com seu raciocínio clínico único.'\n\n"
            "**4. Pergunta para Reflexão (Pergunta Final):** Termine com uma única pergunta aberta e reflexiva que incentive o médico a pensar sobre sua prática. A pergunta deve ser diretamente relacionada aos eventos da semana. Exemplo: 'Houve algum fator específico nesta semana que o levou a confiar mais na sua intuição clínica?' ou 'Qual caso desta semana mais desafiou seu raciocínio?'"
        )
        return prompt

    def gerar_relatorio_semanal(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> str:
        if not encontros:
            return "Nenhuma consulta registada para análise."
        
        resumo = self._criar_resumo_dos_encontros(encontros)
        prompt_final = self._gerar_prompt_relatorio_clinico(resumo, nome_medico)
        
        # A chamada à IA permanece a mesma
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Painel Semanal Coach")
        
        return resposta_dict.get("conteudo", "Não foi possível gerar o relatório.")