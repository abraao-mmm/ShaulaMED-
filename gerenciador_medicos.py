# gerenciador_medicos.py
import json
from medico import Medico # Importa nossa classe Medico
from rich.console import Console

console = Console()

class GerenciadorDeMedicos:
    def __init__(self, caminho_arquivo="medicos.json"):
        self.caminho_arquivo = caminho_arquivo
        self.medicos = self._carregar_medicos()
        self.medico_atual = None

    def _carregar_medicos(self) -> dict:
        """Carrega os perfis dos médicos do arquivo JSON."""
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                dados_medicos = json.load(f)
                # Converte cada dicionário de volta para um objeto Medico
                return {mid: Medico.de_dict(mdata) for mid, mdata in dados_medicos.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {} # Retorna um dicionário vazio se o arquivo não existir

    def salvar_medicos(self):
        """Salva todos os perfis de médicos no arquivo JSON."""
        dados_para_salvar = {mid: m.para_dict() for mid, m in self.medicos.items()}
        with open(self.caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)
        print(f"Perfis dos médicos salvos em '{self.caminho_arquivo}'.")

    def definir_medico_atual(self, nome_medico: str, crm: str, especialidade: str):
        """
        Encontra um médico pelo CRM ou cria um novo perfil se não existir.
        O CRM é um identificador mais seguro que o nome.
        """
        for medico in self.medicos.values():
            if medico.crm == crm:
                self.medico_atual = medico
                console.print(f"Perfil encontrado. Bem-vindo(a) de volta, Dr(a). {medico.nome}.")
                return medico
        
        # Se não encontrou, cria um novo
        console.print(f"CRM não encontrado. Criando novo perfil para Dr(a). {nome_medico}.")
        novo_medico = Medico(nome=nome_medico, crm=crm, especialidade=especialidade)
        self.medicos[novo_medico.id] = novo_medico
        self.medico_atual = novo_medico
        self.salvar_medicos()
        return novo_medico