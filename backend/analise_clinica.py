# analise_clinica.py (Versão com Tom Profissional e Diálogo)

from typing import List, Callable, Dict, Any
from encontro_clinico import EncontroClinico

class MotorDeAnaliseClinica:
    def __init__(self):
        print("Motor de Análise Clínica (Coach Profissional) inicializado.")

    def _preparar_dados_estruturados(self, encontros: List[EncontroClinico]) -> Dict[str, Any]:
        # ... (esta função permanece exatamente a mesma da versão anterior, não precisa alterar)
        dados_tabela = []
        casos_com_divergencia = []
        concordancias = 0
        temas_clinicos = []

        for i, enc in enumerate(encontros):
            hipotese_ia = enc.sugestao_ia.get("hipoteses_diagnosticas", ["N/A"])[0]
            temas_clinicos.append(hipotese_ia)
            decisao_medico = enc.decisao_medico_final
            
            concorda = hipotese_ia.lower() in decisao_medico.lower()
            if concorda:
                concordancias += 1
            else:
                resumo_divergencia = f"no caso sobre '{hipotese_ia}', a decisão foi '{decisao_medico}'"
                # Guarda o ID da consulta para o diálogo
                casos_com_divergencia.append({"resumo": resumo_divergencia, "id": enc.id})

            dados_tabela.append({
                "Caso": f"Consulta {i+1}",
                "Hipótese da IA": hipotese_ia,
                "Decisão do Médico": decisao_medico,
                "Concordância": "✅ Sim" if not concorda else "❌ Não"
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
            "exemplo_divergencia": casos_com_divergencia[0] if casos_com_divergencia else None,
            "temas_predominantes": list(set(temas_clinicos))
        }

    def _gerar_prompt_relatorio_clinico(self, nome_medico: str, dados: Dict[str, Any]) -> str:
        # --- NOVO PROMPT: MAIS DIRETO E PROFISSIONAL ---
        prompt = (
            f"Você é a Shaula, uma IA coach clínica para o(a) Dr(a). {nome_medico}. "
            "Sua tarefa é gerar um 'Painel Semanal' com insights baseados em dados. Use um tom profissional, direto e construtivo.\n\n"
            f"### DADOS DA SEMANA:\n"
            f"- Total de casos: {dados['stats_semanais']['Total de Casos Analisados']}\n"
            f"- Número de diagnósticos diferentes investigados: {dados['stats_semanais']['Novos Diagnósticos Investigados']}\n\n"
            "### ESTRUTURA DO SEU PAINEL (siga estes 3 pontos):\n\n"
            "**1. Padrão de Destaque da Semana:** Com base nos dados, aponte um padrão clínico observado. Exemplo: 'Notei um foco em casos gastrointestinais esta semana, com {X} diagnósticos diferentes nessa área. Isso demonstra uma ampliação do seu escopo investigativo.'\n\n"
            "**2. Ponto para Calibração (Diálogo):** Se houver um caso de divergência, inicie um diálogo para entender o raciocínio. Seja direto e focado no aprendizado. Exemplo: 'No caso sobre {tema}, sua decisão divergiu da sugestão inicial. Para me ajudar a calibrar, qual fator foi determinante para sua escolha?'\n\n"
            "**3. Sugestão de Estudo (Opcional):** Se relevante, sugira UMA diretriz ou artigo baseado nos temas da semana."
        )
        return prompt

    def gerar_relatorio_semanal_completo(self, encontros: List[EncontroClinico], nome_medico: str, obter_resposta_llm_func: Callable) -> Dict[str, Any]:
        # ... (esta função permanece exatamente a mesma, não precisa alterar)
        if not encontros:
            return {"texto_coach": "Nenhuma consulta registada...", "dados_estruturados": None}
        dados_estruturados = self._preparar_dados_estruturados(encontros)
        prompt_final = self._gerar_prompt_relatorio_clinico(nome_medico=nome_medico, dados=dados_estruturados)
        resposta_dict = obter_resposta_llm_func(prompt_final, modo="Painel Semanal Profissional")
        texto_coach = resposta_dict.get("conteudo", "Não foi possível gerar a análise.")
        return {"texto_coach": texto_coach, "dados_estruturados": dados_estruturados}