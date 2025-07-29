# analise_clinica.py (Versão Final com Diálogo Reflexivo e Metáforas)

from typing import List, Callable, Dict, Any
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica (Coach Filósofo 2.0) inicializado.")

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
                # Prepara um resumo do caso divergente para a IA usar
                resumo_divergencia = f"No caso sobre '{hipotese_ia}', você optou por '{decisao_medico}'."
                casos_com_divergencia.append(resumo_divergencia)

            dados_tabela.append({
                "Caso": f"Consulta {i+1}",
                "Hipótese da IA": hipotese_ia,
                "Decisão do Médico": decisao_medico,
                "Concordância": "✅ Sim" if divergencia == 0 else "❌ Não"
            })
            
        total_casos = len(encontros)
        percentual_concordancia = (concordancias / total_casos * 100) if total_casos > 0 else 0
        
        diagnosticos_novos = len(set(temas_clinicos))

        return {
            "tabela_concordancia": dados_tabela,
            "stats_semanais": {
                "% de Concordância com IA": round(percentual_concordancia, 2),
                "Total de Casos Analisados": total_casos,
                "Novos Diagnósticos Investigados": diagnosticos_novos
            },
            # Passa o primeiro caso divergente como exemplo para o prompt
            "exemplo_divergencia": casos_com_divergencia[0] if casos_com_divergencia else None,
            "temas_predominantes": list(set(temas_clinicos))
        }

    def _gerar_prompt_relatorio_clinico(self, nome_medico: str, dados: Dict[str, Any]) -> str:
        prompt = (
            f"Você é a Shaula, uma IA coach clínica com uma veia filosófica, parceira do(a) Dr(a). {nome_medico}. "
            "Sua tarefa é gerar um 'Painel Semanal' que use metáforas para descrever a prática da semana e inicie um diálogo reflexivo. "
            "Seja concisa, inspiradora e use um tom pessoal.\n\n"
            f"### DADOS DA SEMANA:\n"
            f"- Temas clínicos abordados: {', '.join(dados['temas_predominantes'])}\n"
            f"- Exemplo de caso onde a decisão do médico divergiu da sua: {dados['exemplo_divergencia']}\n\n"
            "### ESTRUTURA DO SEU PAINEL (siga estes 3 pontos):\n\n"
            "**1. A Metáfora da Semana:** Comece com uma metáfora visual para descrever a prática da semana. Use a ideia de um 'mapa clínico'. Exemplo: 'Sua prática clínica esta semana foi como explorar um novo continente no seu mapa. Você navegou por {X} regiões diferentes (diagnósticos), mostrando uma grande versatilidade.'\n\n"
            "**2. Início do Diálogo Reflexivo:** Com base no exemplo de divergência fornecido, inicie uma conversa de forma curiosa e não acusatória. O objetivo é aprender com o médico. Exemplo: 'Notei que no caso sobre {tema}, você seguiu um caminho diferente da minha sugestão. Fiquei curiosa, qual foi o seu raciocínio? (Sinta-se à vontade para responder ou apenas refletir).'\n\n"
            "**3. Mensagem de Encerramento Simbólica:** Termine com uma única frase filosófica e encorajadora sobre a prática da medicina. Exemplo: 'Cada decisão clínica é um ponto de luz no vasto mapa do cuidado. Continue a iluminá-lo.'"
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