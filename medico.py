# medico.py

class Medico:
    """
    Representa um médico no sistema ShaulaMed, com seu estilo clínico sendo
    continuamente aprendido pela IA.
    """
    def __init__(self, nome: str, crm: str, especialidade: str):
        self.id = f"{crm.replace('.', '').replace('-', '')}_{especialidade.lower()}"
        self.nome = nome
        self.crm = crm
        self.especialidade = especialidade
        self.nivel_confianca_ia: int = 1 
        self.estilo_clinico_observado = {
            "padrao_prescritivo": {},
            "exames_mais_solicitados": set(), # Usamos set para evitar duplicados
            "linguagem_resumo": "SOAP"
        }
        self.consultas_realizadas_count: int = 0

    def aprender_com_conduta(self, diagnostico_principal: str, conduta_final: str):
        if not diagnostico_principal or not conduta_final:
            return
        self.estilo_clinico_observado["padrao_prescritivo"][diagnostico_principal] = conduta_final

    # --- MÉTODO CORRIGIDO QUE ESTAVA FALTANDO ---
    def para_dict(self):
        """Converte o objeto para um dicionário para salvar em JSON."""
        # Copiamos o dicionário para não modificar o original
        estilo_serializavel = self.estilo_clinico_observado.copy()
        # Convertemos o 'set' para uma 'list' para que ele possa ser salvo em JSON
        estilo_serializavel['exames_mais_solicitados'] = list(self.estilo_clinico_observado['exames_mais_solicitados'])
        
        return {
            "id": self.id,
            "nome": self.nome,
            "crm": self.crm,
            "especialidade": self.especialidade,
            "nivel_confianca_ia": self.nivel_confianca_ia,
            "estilo_clinico_observado": estilo_serializavel,
            "consultas_realizadas_count": self.consultas_realizadas_count
        }

    # --- MÉTODO CORRIGIDO QUE ESTAVA FALTANDO ---
    @staticmethod
    def de_dict(data: dict):
        """Cria um objeto Medico a partir de um dicionário (carregado do JSON)."""
        medico = Medico(
            nome=data.get('nome', 'N/A'),
            crm=data.get('crm', '0000'),
            especialidade=data.get('especialidade', 'clínica geral')
        )
        medico.id = data.get('id')
        medico.nivel_confianca_ia = data.get('nivel_confianca_ia', 1)
        
        estilo_carregado = data.get('estilo_clinico_observado', {})
        medico.estilo_clinico_observado['padrao_prescritivo'] = estilo_carregado.get('padrao_prescritivo', {})
        # Convertemos a 'list' do JSON de volta para um 'set'
        medico.estilo_clinico_observado['exames_mais_solicitados'] = set(estilo_carregado.get('exames_mais_solicitados', []))
        medico.estilo_clinico_observado['linguagem_resumo'] = estilo_carregado.get('linguagem_resumo', 'SOAP')
        
        medico.consultas_realizadas_count = data.get('consultas_realizadas_count', 0)
        return medico