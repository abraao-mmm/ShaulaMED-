# gerenciador_medicos.py (Versão Final e Robusta)

import firebase_admin
from firebase_admin import credentials, firestore
from medico import Medico
from rich.console import Console

console = Console()

class GerenciadorDeMedicos:
    def __init__(self, caminho_credenciais="firebase-credentials.json"):
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(f"/etc/secrets/{caminho_credenciais}")
                firebase_admin.initialize_app(cred)
                console.print("[green]Conexão com o Firebase (Servidor) estabelecida.[/green]")
            except Exception:
                try:
                    cred = credentials.Certificate(caminho_credenciais)
                    firebase_admin.initialize_app(cred)
                    console.print("[green]Conexão com o Firebase (Local) estabelecida.[/green]")
                except Exception as e_local:
                    console.print(f"[bold red]ERRO CRÍTICO: Não foi possível conectar ao Firebase.[/bold red]")
                    raise e_local

        self.db = firestore.client()
        self.medicos_ref = self.db.collection('medicos')

    def carregar_ou_criar_perfil(self, utilizador_auth: dict) -> Medico:
        uid = utilizador_auth.get('localId')
        email = utilizador_auth.get('email')
        
        if not uid:
            raise ValueError("Dados de autenticação inválidos, UID não encontrado.")

        try:
            doc_ref = self.medicos_ref.document(uid)
            doc = doc_ref.get()
            
            if doc.exists:
                console.print(f"Perfil do médico com email '{email}' carregado do Firestore.")
                return Medico.de_dict(uid, doc.to_dict())
            else:
                # --- LÓGICA DE FALLBACK (SE O PERFIL NÃO EXISTIR) ---
                console.print(f"[yellow]Aviso: Perfil para UID {uid} não encontrado. A criar um perfil básico.[/yellow]")
                novo_medico = Medico(
                    uid=uid,
                    email=email,
                    nome_completo=email.split('@')[0], # Usa o início do email como nome temporário
                    crm="0000",
                    especialidade="Não definida"
                )
                doc_ref.set(novo_medico.para_dict())
                console.print("Perfil básico criado no Firestore.")
                return novo_medico
        except Exception as e:
            console.print(f"[bold red]Erro ao carregar ou criar perfil no Firestore:[/bold red] {e}")
            return None

    def salvar_medico(self, medico: Medico):
        try:
            self.medicos_ref.document(medico.id).set(medico.para_dict())
            console.print(f"Perfil do Dr(a). {medico.nome_completo} salvo no Firestore.")
        except Exception as e:
            console.print(f"[bold red]Erro ao salvar perfil no Firestore:[/bold red] {e}")