# medico.py

class Medico:
    def __init__(self, uid: str, email: str, nome_completo: str, crm: str, especialidade: str, apelido: str = "", sexo: str = ""):
        self.id = uid
        self.email = email
        self.nome_completo = nome_completo
        self.crm = crm
        self.especialidade = especialidade
        self.apelido = apelido if apelido else nome_completo.split(" ")[0]
        self.sexo = sexo

        # --- NOVOS ATRIBUTOS ADICIONADOS AQUI ---
        # Por padrão, todo novo médico começa no plano de teste.
        self.plano_assinatura = "essencial_teste" # Opções: "essencial_teste", "pro"

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
            "plano_assinatura": self.plano_assinatura, # Adicionado para salvar
            "nivel_confianca_ia": self.nivel_confianca_ia,
            "estilo_clinico_observado": estilo_serializavel,
            "consultas_realizadas_count": self.consultas_realizadas_count
        }

    @staticmethod
    def de_dict(uid: str, data: dict):
        medico = Medico(
            uid=uid,
            email=data.get('email', ''),
            nome_completo=data.get('nome_completo', 'N/A'),
            crm=data.get('crm', '0000'),
            especialidade=data.get('especialidade', 'clínica geral'),
            apelido=data.get('apelido', ''),
            sexo=data.get('sexo', '')
        )
        # Adicionado para carregar o plano do Firestore
        medico.plano_assinatura = data.get('plano_assinatura', 'essencial_teste')

        medico.nivel_confianca_ia = data.get('nivel_confianca_ia', 1)

        estilo_carregado = data.get('estilo_clinico_observado', {})
        medico.estilo_clinico_observado['padrao_prescritivo'] = estilo_carregado.get('padrao_prescritivo', {})
        medico.estilo_clinico_observado['exames_mais_solicitados'] = set(estilo_carregado.get('exames_mais_solicitados', []))
        medico.estilo_clinico_observado['linguagem_resumo'] = estilo_carregado.get('linguagem_resumo', 'SOAP')

        medico.consultas_realizadas_count = data.get('consultas_realizadas_count', 0)
        return medico