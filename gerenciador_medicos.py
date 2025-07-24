# gerenciador_medicos.py (Versão Corrigida)

import firebase_admin
from firebase_admin import credentials, firestore
from medico import Medico
from rich.console import Console

console = Console()

class GerenciadorDeMedicos:
    # --- ALTERAÇÃO AQUI ---
    # O caminho para as credenciais agora aponta para a pasta de segredos do Render.
    def __init__(self, caminho_credenciais="/etc/secrets/firebase-credentials.json"):
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(caminho_credenciais)
                firebase_admin.initialize_app(cred)
                console.print("[green]Conexão com o Firebase estabelecida com sucesso.[/green]")
            except Exception as e:
                # Se falhar, tentamos o caminho local (para continuar a funcionar no seu computador)
                try:
                    cred = credentials.Certificate("firebase-credentials.json")
                    firebase_admin.initialize_app(cred)
                    console.print("[green]Conexão com o Firebase (local) estabelecida com sucesso.[/green]")
                except Exception as e_local:
                    console.print(f"[bold red]ERRO: Não foi possível conectar ao Firebase.[/bold red]\n{e_local}")
                    raise e_local

        self.db = firestore.client()
        self.medicos_ref = self.db.collection('medicos')
        self.medico_atual = None

    def carregar_ou_criar_perfil(self, utilizador_auth: dict) -> Medico:
        """
        Carrega o perfil de um médico do Firestore usando o UID da autenticação.
        Se o perfil não existir, ele não faz nada (o perfil deveria ter sido criado no registo).
        """
        uid = utilizador_auth.get('localId')
        email = utilizador_auth.get('email')
        
        if not uid:
            raise ValueError("Dados de autenticação inválidos, UID não encontrado.")

        try:
            doc = self.medicos_ref.document(uid).get()
            if doc.exists:
                console.print(f"Perfil do médico com email '{email}' carregado do Firestore.")
                medico = Medico.de_dict(uid, doc.to_dict())
                self.medico_atual = medico
                return medico
            else:
                console.print(f"[yellow]Aviso: Utilizador autenticado mas sem perfil no Firestore. Pode ser um novo registo.[/yellow]")
                # Em um fluxo real, poderíamos redirecionar para completar o perfil aqui.
                return None
        except Exception as e:
            console.print(f"[bold red]Erro ao carregar perfil do Firestore:[/bold red] {e}")
            return None