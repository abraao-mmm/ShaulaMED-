# encontro_clinico.py
from datetime import datetime

class EncontroClinico:
    """
    Registra todos os dados de uma única consulta, servindo como a unidade
    fundamental de memória para o aprendizado e reflexão do ShaulaMed.
    """
    def __init__(self, medico_id: str, transcricao_consulta: str):
        self.id = f"enc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.timestamp = datetime.now()
        self.medico_id = medico_id
        self.transcricao_consulta = transcricao_consulta 
        self.sugestao_ia: dict = {}
        self.decisao_medico_final: str = ""
        self.texto_gerado_prontuario: str = ""
        self.contexto_emocional_paciente: str = "neutro"
        self.desvio_de_padrao: bool = False
        self.reflexao_ia: str = ""

    def para_dict(self):
        """Converte o objeto para um dicionário para salvar em JSON."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "medico_id": self.medico_id,
            "transcricao_consulta": self.transcricao_consulta,
            "sugestao_ia": self.sugestao_ia,
            "decisao_medico_final": self.decisao_medico_final,
            "texto_gerado_prontuario": self.texto_gerado_prontuario,
            "contexto_emocional_paciente": self.contexto_emocional_paciente,
            "desvio_de_padrao": self.desvio_de_padrao,
            "reflexao_ia": self.reflexao_ia
        }
    
    # Dentro da classe EncontroClinico, no ficheiro encontro_clinico.py

    @staticmethod
    def de_dict(data: dict):
        """Cria um objeto EncontroClinico a partir de um dicionário."""
        # Criamos um objeto vazio, pois a transcrição é necessária no construtor
        encontro = EncontroClinico(
            medico_id=data.get('medico_id'),
            transcricao_consulta=data.get('transcricao_consulta')
        )
        # Preenchemos os restantes campos a partir dos dados
        encontro.id = data.get('id')
        encontro.timestamp = datetime.fromisoformat(data.get('timestamp'))
        encontro.sugestao_ia = data.get('sugestao_ia', {})
        encontro.decisao_medico_final = data.get('decisao_medico_final', "")
        encontro.texto_gerado_prontuario = data.get('texto_gerado_prontuario', "")
        encontro.contexto_emocional_paciente = data.get('contexto_emocional_paciente', "neutro")
        encontro.desvio_de_padrao = data.get('desvio_de_padrao', False)
        encontro.reflexao_ia = data.get('reflexao_ia', "")
        return encontro