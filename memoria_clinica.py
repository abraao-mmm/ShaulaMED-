# memoria_clinica.py
import json
from encontro_clinico import EncontroClinico
from typing import List

class MemoriaClinica:
    def __init__(self):
        self.encontros: List[EncontroClinico] = []

    def registrar_encontro(self, encontro: EncontroClinico):
        self.encontros.append(encontro)
        print(f"Memória: Encontro Clínico '{encontro.id}' registrado com sucesso.")

    def carregar_de_json(self, caminho_arquivo: str = "memoria_clinica.json"):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                pass
            print(f"Memória carregada de '{caminho_arquivo}'.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Arquivo de memória não encontrado. Começando com memória limpa.")

    def exportar_para_json(self, caminho_arquivo: str = "memoria_clinica.json"):
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                dados_serializados = [e.para_dict() for e in self.encontros]
                json.dump(dados_serializados, f, indent=4, ensure_ascii=False)
            print(f"Memória salva com sucesso em '{caminho_arquivo}'.")
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")