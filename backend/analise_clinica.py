# analise_clinica.py (Versão com Saída Estruturada para Gráficos)

from typing import List, Callable, Dict, Any
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica (Coach + Dados Estruturados) inicializado.")

    def _preparar_dados_estruturados(self, encontros: List[EncontroClinico]) -> Dict[str, Any]:
        """
        Analisa os encontros e extrai dados numéricos e para a tabela.
        """
        dados_tabela = []
        concordancias = 0
        
        for i, enc in enumerate(encontros):
            hipotese_ia = enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0]
            decisao_medico = enc.decisao_medico_final
            
            concorda = hipotese_ia.lower() in decisao_medico.lower()
            if concorda:
                concordancias += 1

            dados_tabela.append({
                "Caso": f"Consulta {i+1}",
                "Hipótese da IA": hipotese_ia,
                "Decisão do Médico": decisao_medico,
                "Concordância": "✅ Sim" if concorda else "❌ Não"
            })
            
        total_casos = len(encontros)
        percentual_concordancia = (concordancias / total_casos * 100) if total_casos > 0 else 0
        
        dados_grafico = {
            "% de Concordância com IA": round(percentual_concordancia, 2),
            "Total de Casos Analisados": total_casos,
        }
        
        return {
            "tabela_concordancia": dados_tabela,
            "stats_semanais": dados_grafico
        }

    def _gerar_prompt_relatorio_clinico(self, nome_medico: str) -> str:
        """
        Prompt simplificado, pois a análise de dados brutos agora é feita em Python.
        """
        prompt = (
            f"Você é a Shaula, uma IA que atua como uma coach clínica para o(a) Dr(a). {nome_medico}. "
            "Gere um texto curto (2-3 frases) de análise e encorajamento sobre a semana de trabalho, "
            "e termine com uma pergunta reflexiva."
        )
        return prompt

    def gerar_relatorio_semanal_completo(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> Dict[str, Any]:
        if not encontros:
            return {
                "texto_coach": "Nenhuma consulta registada na última semana para análise.",
                "dados_estruturados": None
            }
        
        # 1. Gera o texto do coach com a IA
        prompt_final = self._gerar_prompt_relatorio_clinico(nome_medico)
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Painel Semanal Coach")
        texto_coach = resposta_dict.get("conteudo", "Não foi possível gerar a análise da semana.")
        
        # 2. Prepara os dados estruturados com Python
        dados_estruturados = self._preparar_dados_estruturados(encontros)
        
        # 3. Combina tudo numa única resposta JSON
        return {
            "texto_coach": texto_coach,
            "dados_estruturados": dados_estruturados
        }