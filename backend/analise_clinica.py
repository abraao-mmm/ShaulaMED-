# analise_clinica.py (Versão com Casos Notáveis e Sugestão de Estudo)

from typing import List, Callable, Dict, Any
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica (Coach Avançado) inicializado.")

    def _calcular_divergencia(self, hipotese_ia: str, decisao_medico: str) -> int:
        """
        Calcula um score de divergência simples. 
        Retorna 0 para concordância, 1 para divergência.
        """
        return 0 if hipotese_ia.lower() in decisao_medico.lower() else 1

    def _preparar_dados_estruturados(self, encontros: List[EncontroClinico]) -> Dict[str, Any]:
        dados_tabela = []
        casos_com_divergencia = []
        concordancias = 0
        temas_clinicos = []

        for i, enc in enumerate(encontros):
            hipotese_ia = enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0]
            temas_clinicos.append(hipotese_ia)
            decisao_medico = enc.decisao_medico_final
            
            divergencia = self._calcular_divergencia(hipotese_ia, decisao_medico)
            if divergencia == 0:
                concordancias += 1
            else:
                casos_com_divergencia.append(f"Consulta {i+1} (Sua decisão: '{decisao_medico}', Sugestão IA: '{hipotese_ia}')")

            dados_tabela.append({
                "Caso": f"Consulta {i+1}",
                "Hipótese da IA": hipotese_ia,
                "Decisão do Médico": decisao_medico,
                "Concordância": "✅ Sim" if divergencia == 0 else "❌ Não"
            })
            
        total_casos = len(encontros)
        percentual_concordancia = (concordancias / total_casos * 100) if total_casos > 0 else 0
        
        # Identifica os casos notáveis
        caso_mais_concordante = "Todos os casos tiveram alguma divergência."
        if concordancias > 0:
            caso_mais_concordante = "Pelo menos um caso teve diagnóstico e conduta alinhados com a sugestão inicial."
        
        caso_mais_divergente = "Não houve divergências significativas esta semana."
        if casos_com_divergencia:
            caso_mais_divergente = casos_com_divergencia[0] # Pega o primeiro caso divergente como exemplo

        return {
            "tabela_concordancia": dados_tabela,
            "stats_semanais": {
                "% de Concordância com IA": round(percentual_concordancia, 2),
                "Total de Casos Analisados": total_casos,
            },
            "casos_notaveis": {
                "mais_concordante": caso_mais_concordante,
                "mais_divergente": caso_mais_divergente
            },
            "temas_predominantes": list(set(temas_clinicos)) # Lista de temas únicos para a sugestão de estudo
        }

    def _gerar_prompt_relatorio_clinico(self, nome_medico: str, casos_notaveis: Dict[str, str], temas: List[str]) -> str:
        prompt = (
            f"Você é a Shaula, uma IA coach clínica para o(a) Dr(a). {nome_medico}. "
            "Sua tarefa é gerar um 'Painel Semanal' com insights e sugestões de estudo. "
            "Seja concisa e use um tom pessoal.\n\n"
            f"### DESTAQUES DA SEMANA (Análise pré-processada):\n"
            f"- Caso mais concordante: {casos_notaveis['mais_concordante']}\n"
            f"- Caso mais divergente: {casos_notaveis['mais_divergente']}\n"
            f"- Temas clínicos abordados: {', '.join(temas)}\n\n"
            "### ESTRUTURA DO SEU PAINEL (siga estes 3 pontos):\n\n"
            "**1. Destaques da Semana:** Com base nos destaques fornecidos, escreva um parágrafo curto (2-3 frases) comentando sobre o caso mais divergente ou o mais concordante, de forma construtiva.\n\n"
            "**2. Sugestão de Estudo Personalizada:** Com base nos temas clínicos da semana, sugira UM tópico de estudo ou a leitura de UMA diretriz recente que seja relevante. Seja específico. Exemplo: 'Sugestão de leitura: Diretriz da SBEM sobre abordagem de refluxo 2023.'\n\n"
            "**3. Pergunta para Reflexão:** Termine com uma única pergunta aberta e reflexiva sobre a prática da semana."
        )
        return prompt

    def gerar_relatorio_semanal_completo(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> Dict[str, Any]:
        if not encontros:
            return {
                "texto_coach": "Nenhuma consulta registada na última semana para análise.",
                "dados_estruturados": None
            }
        
        # 1. Prepara os dados estruturados e identifica casos notáveis PRIMEIRO
        dados_estruturados = self._preparar_dados_estruturados(encontros)
        
        # 2. Gera o prompt da IA usando os dados extraídos
        prompt_final = self._gerar_prompt_relatorio_clinico(
            nome_medico=nome_medico,
            casos_notaveis=dados_estruturados['casos_notaveis'],
            temas=dados_estruturados['temas_predominantes']
        )
        
        # 3. Gera o texto do coach com a IA
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Painel Semanal Coach Avançado")
        texto_coach = resposta_dict.get("conteudo", "Não foi possível gerar a análise da semana.")
        
        # 4. Combina tudo numa única resposta JSON
        return {
            "texto_coach": texto_coach,
            "dados_estruturados": dados_estruturados
        }