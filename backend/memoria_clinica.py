# memoria_clinica.py (Versão Firestore)

import firebase_admin
from firebase_admin import firestore
from encontro_clinico import EncontroClinico
from typing import List
from rich.console import Console

console = Console()

class MemoriaClinica:
    """
    Gerencia o armazenamento e a recuperação de todos os encontros clínicos (consultas)
    usando o banco de dados Firestore.
    """
    def __init__(self):
        # A conexão com o Firebase já foi iniciada pelo GerenciadorDeMedicos,
        # então apenas obtemos uma referência para o serviço de banco de dados.
        self.db = firestore.client()
        # Aponta para a "gaveta" (coleção) onde os encontros clínicos serão guardados
        self.consultas_ref = self.db.collection('consultas')
        
        # A memória em tempo de execução agora é carregada sob demanda ou pode ser mantida em cache
        self.encontros_em_memoria: List[EncontroClinico] = []
        console.print("[green]Módulo de Memória Clínica conectado ao Firestore.[/green]")

    def registrar_encontro(self, encontro: EncontroClinico):
        """Adiciona um novo encontro clínico ao Firestore."""
        try:
            # Usa o ID do encontro para criar um novo documento na coleção 'consultas'
            self.consultas_ref.document(encontro.id).set(encontro.para_dict())
            # Adiciona também à memória local para uso imediato (ex: relatórios)
            self.encontros_em_memoria.append(encontro)
            console.print(f"Memória: Encontro Clínico '{encontro.id}' registado no Firestore com sucesso.")
        except Exception as e:
            console.print(f"[bold red]Erro ao registar encontro no Firestore:[/bold red] {e}")

    def carregar_encontros_do_medico(self, medico_id: str):
        """
        Carrega todos os encontros de um médico específico do Firestore para a memória local.
        """
        try:
            console.print(f"A carregar histórico de consultas do Dr. ID {medico_id} do Firestore...")
            # Cria uma consulta para encontrar todos os documentos onde 'medico_id' corresponde
            docs = self.consultas_ref.where('medico_id', '==', medico_id).stream()
            
            self.encontros_em_memoria = [] # Limpa a memória atual
            for doc in docs:
                # Precisamos de um método EncontroClinico.de_dict() para isto funcionar
                # Vamos assumir que ele existe por agora
                self.encontros_em_memoria.append(EncontroClinico.de_dict(doc.to_dict()))

            console.print(f"{len(self.encontros_em_memoria)} consultas carregadas para a memória.")
        except Exception as e:
            console.print(f"[bold red]Erro ao carregar encontros do Firestore:[/bold red] {e}")