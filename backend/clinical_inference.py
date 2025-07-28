# clinical_inference.py

class SimulatedInferenceEngine:
    def __init__(self):
        print("Motor de Inferência Clínica (Simulado) inicializado.")
        self.mapa_sintomas = {
            "dor de garganta": "faringite",
            "febre": "infecção",
            "tosse": "infecção respiratória",
            "coriza": "infecção respiratória",
            "dor de cabeça": "cefaleia",
            "queimação no estômago": "dispepsia",
            "enjoo": "náusea"
        }

    def extrair_sintomas(self, texto_consulta: str) -> list[str]:
        sintomas_encontrados = []
        texto_lower = texto_consulta.lower()
        for palavra_chave, sintoma in self.mapa_sintomas.items():
            if palavra_chave in texto_lower and sintoma not in sintomas_encontrados:
                sintomas_encontrados.append(sintoma)
        return sintomas_encontrados

    def gerar_hipoteses(self, sintomas: list[str]) -> dict:
        if not sintomas:
            return {}
        if "faringite" in sintomas and "infecção" in sintomas:
            return {
                "hipoteses": ["Faringoamigdalite Aguda", "Faringite Viral", "Faringite Estreptocócica"],
                "conduta_sugerida": "Aplicar escore de Centor para avaliar risco de Streptococcus. Considerar teste rápido.",
                "fonte": "IDSA Guidelines 2023 (Simulado)"
            }
        if "dispepsia" in sintomas:
            return {
                "hipoteses": ["Dispepsia Funcional", "DRGE", "Gastrite"],
                "conduta_sugerida": "Pesquisar por H. pylori com teste respiratório.",
                "fonte": "WGO 2024 (Simulado)"
            }
        return {
            "hipoteses": ["Virose Inespecífica"],
            "conduta_sugerida": "Recomendar repouso, hidratação e sintomáticos.",
            "fonte": "Prática Clínica Geral (Simulado)"
        }