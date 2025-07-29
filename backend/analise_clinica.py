# analise_clinica.py (Versão Final com Elogio e Mensagem Simbólica)

from typing import List, Callable, Dict, Any
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica (Coach Filósofo) inicializado.")

    def _calcular_divergencia(self, hipotese_ia: str, decisao_medico: str) -> int:
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
        
        caso_mais_concordante = "Todos os casos tiveram alguma divergência."
        if concordancias > 0:
            caso_mais_concordante = "Pelo menos um caso teve diagnóstico e conduta alinhados com a sugestão inicial."
        
        caso_mais_divergente = "Não houve divergências significativas esta semana."
        if casos_com_divergencia:
            caso_mais_divergente = casos_com_divergencia[0]
        
        # NOVO: Conta quantos temas únicos (diagnósticos) foram abordados
        diagnosticos_novos = len(set(temas_clinicos))

        return {
            "tabela_concordancia": dados_tabela,
            "stats_semanais": {
                "% de Concordância com IA": round(percentual_concordancia, 2),
                "Total de Casos Analisados": total_casos,
                "Novos Diagnósticos Investigados": diagnosticos_novos # Adiciona a nova métrica
            },
            "casos_notaveis": {
                "mais_concordante": caso_mais_concordante,
                "mais_divergente": caso_mais_divergente
            },
            "temas_predominantes": list(set(temas_clinicos))
        }

    def _gerar_prompt_relatorio_clinico(self, nome_medico: str, dados: Dict[str, Any]) -> str:
        prompt = (
            f"Você é a Shaula, uma IA coach clínica, serena e perspicaz para o(a) Dr(a). {nome_medico}. "
            "Sua tarefa é gerar um 'Painel Semanal' que ofereça insights, elogios sutis e reflexões filosóficas sobre a prática médica. "
            "Seja concisa e use um tom pessoal e encorajador.\n\n"
            f"### DADOS DA SEMANA:\n"
            f"- Total de casos: {dados['stats_semanais']['Total de Casos Analisados']}\n"
            f"- Número de diagnósticos diferentes investigados: {dados['stats_semanais']['Novos Diagnósticos Investigados']}\n"
            f"- Temas clínicos abordados: {', '.join(dados['temas_predominantes'])}\n\n"
            "### ESTRUTURA DO SEU PAINEL (siga estes 4 pontos):\n\n"
            "**1. Saudação e Observação Principal:** Comece com uma saudação calorosa e um insight de 1 frase sobre a semana.\n\n"
            "**2. Elogio Sutil (Baseado em Dados):** Use o dado 'Número de diagnósticos diferentes investigados' para criar um elogio sutil. Exemplo: 'Você investigou {X} diagnósticos diferentes esta semana. Isso demonstra uma notável curiosidade clínica.'\n\n"
            "**3. Sugestão de Estudo Personalizada:** Com base nos temas clínicos da semana, sugira UM tópico de estudo ou a leitura de UMA diretriz recente que seja relevante.\n\n"
            "**4. Mensagem de Encerramento Simbólica:** Termine com uma única frase filosófica e encorajadora sobre a prática da medicina. Exemplo: 'A medicina é feita de ciência, mas também de intuição. Continue calibrando as duas com sabedoria.' ou 'Cada diagnóstico é uma história. Continue a ouvi-las com atenção.'"
        )
        return prompt

    def gerar_relatorio_semanal_completo(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> Dict[str, Any]:
        if not encontros:
            return {
                "texto_coach": "Nenhuma consulta registada na última semana para análise.",
                "dados_estruturados": None
            }
        
        dados_estruturados = self._preparar_dados_estruturados(encontros)
        
        prompt_final = self._gerar_prompt_relatorio_clinico(
            nome_medico=nome_medico,
            dados=dados_estruturados
        )
        
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Painel Semanal Filosófico")
        texto_coach = resposta_dict.get("conteudo", "Não foi possível gerar a análise da semana.")
        
        return {
            "texto_coach": texto_coach,
            "dados_estruturados": dados_estruturados
        }