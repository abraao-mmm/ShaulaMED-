# memoria_clinica.py (Versão com Subconjuntos)

import firebase_admin
from firebase_admin import firestore
from encontro_clinico import EncontroClinico
from typing import List
from rich.console import Console

console = Console()

class MemoriaClinica:
    """
    Gerencia o armazenamento e a recuperação de encontros clínicos
    usando uma subcoleção dentro do documento de cada médico no Firestore.
    """
    def __init__(self, medico_id: str):
        if not medico_id:
            raise ValueError("O ID do médico é necessário para inicializar a Memória Clínica.")
            
        self.db = firestore.client()
        # O caminho agora aponta para a subcoleção de consultas DENTRO de um médico específico.
        self.consultas_ref = self.db.collection('medicos').document(medico_id).collection('consultas')
        
        self.encontros_em_memoria: List[EncontroClinico] = []
        console.print(f"[green]Módulo de Memória conectado à subcoleção do médico ID: {medico_id}[/green]")

        # Carrega o histórico ao ser inicializado
        self.carregar_encontros_do_medico()

    def registrar_encontro(self, encontro: EncontroClinico):
        """Adiciona um novo encontro clínico à subcoleção do médico no Firestore."""
        try:
            # O caminho já está correto, basta criar o documento
            self.consultas_ref.document(encontro.id).set(encontro.para_dict())
            self.encontros_em_memoria.append(encontro)
            console.print(f"Memória: Encontro Clínico '{encontro.id}' registado na subcoleção com sucesso.")
        except Exception as e:
            console.print(f"[bold red]Erro ao registar encontro na subcoleção:[/bold red] {e}")

    def carregar_encontros_do_medico(self):
        """Carrega todos os encontros da subcoleção do médico para a memória local."""
        try:
            console.print(f"A carregar histórico da subcoleção de consultas...")
            # Como a self.consultas_ref já aponta para o lugar certo, basta pedir os documentos.
            docs = self.consultas_ref.stream()
            
            self.encontros_em_memoria = []
            for doc in docs:
                self.encontros_em_memoria.append(EncontroClinico.de_dict(doc.to_dict()))

            console.print(f"{len(self.encontros_em_memoria)} consultas carregadas para a memória.")
        except Exception as e:
            console.print(f"[bold red]Erro ao carregar encontros da subcoleção:[/bold red] {e}")