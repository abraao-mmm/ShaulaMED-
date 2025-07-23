# gerenciador_medicos.py (Versão Firestore)

import firebase_admin
from firebase_admin import credentials, firestore
from medico import Medico
from rich.console import Console

console = Console()

class GerenciadorDeMedicos:
    def __init__(self, caminho_credenciais="firebase-credentials.json"):
        # Verifica se a aplicação Firebase já foi inicializada
        if not firebase_admin._apps:
            try:
                # Usa o ficheiro de credenciais para se autenticar
                cred = credentials.Certificate(caminho_credenciais)
                firebase_admin.initialize_app(cred)
                console.print("[green]Conexão com o Firebase estabelecida com sucesso.[/green]")
            except Exception as e:
                console.print(f"[bold red]ERRO: Não foi possível conectar ao Firebase. Verifique o ficheiro de credenciais.[/bold red]\n{e}")
                raise e

        # Obtém uma referência para o serviço de banco de dados do Firestore
        self.db = firestore.client()
        # Aponta para a "gaveta" (coleção) onde os perfis dos médicos serão guardados
        self.medicos_ref = self.db.collection('medicos')
        
        # Carrega os médicos existentes do Firestore para a memória
        self.medicos = self._carregar_medicos()
        self.medico_atual = None

    def _carregar_medicos(self) -> dict:
        """
        Carrega os perfis dos médicos a partir da coleção do Firestore.
        """
        console.print("A carregar perfis de médicos do Firestore...")
        medicos_carregados = {}
        # Pede ao Firestore todos os "documentos" (perfis) da coleção 'medicos'
        docs = self.medicos_ref.stream()
        for doc in docs:
            medico_obj = Medico.de_dict(doc.to_dict())
            medicos_carregados[medico_obj.id] = medico_obj
        
        console.print(f"{len(medicos_carregados)} perfil(s) de médico(s) carregado(s).")
        return medicos_carregados

    def salvar_medico(self, medico: Medico):
        """
        Salva ou atualiza um único perfil de médico no Firestore.
        """
        try:
            # Usa o ID do médico para criar ou substituir um documento na coleção
            self.medicos_ref.document(medico.id).set(medico.para_dict())
            console.print(f"Perfil do Dr(a). {medico.nome} salvo no Firestore.")
        except Exception as e:
            console.print(f"[bold red]Erro ao salvar perfil no Firestore:[/bold red] {e}")

    def definir_medico_atual(self, nome_medico: str, crm: str, especialidade: str):
        """
        Encontra um médico pelo CRM na memória local ou cria um novo perfil e salva-o no Firestore.
        """
        # Procura na memória local primeiro
        for medico in self.medicos.values():
            if medico.crm == crm:
                self.medico_atual = medico
                console.print(f"Perfil encontrado. Bem-vindo(a) de volta, Dr(a). {medico.nome}.")
                return medico
        
        # Se não encontrou, cria um novo
        console.print(f"CRM não encontrado. A criar novo perfil para Dr(a). {nome_medico}.")
        novo_medico = Medico(nome=nome_medico, crm=crm, especialidade=especialidade)
        self.medicos[novo_medico.id] = novo_medico
        self.medico_atual = novo_medico
        # Salva o novo perfil imediatamente no banco de dados da nuvem
        self.salvar_medico(novo_medico)
        return novo_medico