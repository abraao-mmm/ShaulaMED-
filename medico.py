# medico.py

class Medico:
    """
    Representa um médico no sistema ShaulaMed, com seu perfil completo e
    estilo clínico sendo continuamente aprendido pela IA.
    """

    def __init__(self, uid: str, email: str, nome_completo: str, crm: str, especialidade: str, apelido: str = "", sexo: str = ""):
        # O ID do médico agora é o UID seguro do Firebase Authentication
        self.id = uid
        self.email = email
        self.nome_completo = nome_completo
        self.crm = crm
        self.especialidade = especialidade
        
        # Usa o primeiro nome como apelido se nenhum for fornecido
        self.apelido = apelido if apelido else nome_completo.split(" ")[0]
        self.sexo = sexo
        
        # Atributos que a IA aprende e monitora
        self.nivel_confianca_ia: int = 1 
        self.estilo_clinico_observado = {
            "padrao_prescritivo": {},
            "exames_mais_solicitados": set(),
            "linguagem_resumo": "SOAP"
        }
        self.consultas_realizadas_count: int = 0

    def aprender_com_conduta(self, diagnostico_principal: str, conduta_final: str):
        if not diagnostico_principal or not conduta_final:
            return
        self.estilo_clinico_observado["padrao_prescritivo"][diagnostico_principal] = conduta_final

    def para_dict(self) -> dict:
        """Converte o objeto para um dicionário para salvar no Firestore."""
        estilo_serializavel = self.estilo_clinico_observado.copy()
        estilo_serializavel['exames_mais_solicitados'] = list(self.estilo_clinico_observado['exames_mais_solicitados'])
        
        return {
            "id": self.id,
            "email": self.email,
            "nome_completo": self.nome_completo,
            "crm": self.crm,
            "especialidade": self.especialidade,
            "apelido": self.apelido,
            "sexo": self.sexo,
            "nivel_confianca_ia": self.nivel_confianca_ia,
            "estilo_clinico_observado": estilo_serializavel,
            "consultas_realizadas_count": self.consultas_realizadas_count
        }

    @staticmethod
    def de_dict(uid: str, data: dict):
        """Cria um objeto Medico a partir de um dicionário (carregado do Firestore)."""
        medico = Medico(
            uid=uid,
            email=data.get('email', ''),
            nome_completo=data.get('nome_completo', 'N/A'),
            crm=data.get('crm', '0000'),
            especialidade=data.get('especialidade', 'clínica geral'),
            apelido=data.get('apelido', ''),
            sexo=data.get('sexo', '')
        )
        medico.nivel_confianca_ia = data.get('nivel_confianca_ia', 1)
        
        estilo_carregado = data.get('estilo_clinico_observado', {})
        medico.estilo_clinico_observado['padrao_prescritivo'] = estilo_carregado.get('padrao_prescritivo', {})
        medico.estilo_clinico_observado['exames_mais_solicitados'] = set(estilo_carregado.get('exames_mais_solicitados', []))
        medico.estilo_clinico_observado['linguagem_resumo'] = estilo_carregado.get('linguagem_resumo', 'SOAP')
        
        medico.consultas_realizadas_count = data.get('consultas_realizadas_count', 0)
        return medico