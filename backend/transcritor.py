# transcritor.py

import openai
import os

# Tenta inicializar o cliente OpenAI. A chave deve estar nas variáveis de ambiente do servidor.
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    # Este print aparecerá nos logs do Render se a chave não for encontrada
    print(f"Erro ao inicializar o cliente OpenAI no transcritor: {e}")
    client = None

def transcrever_audio_bytes(audio_bytes):
    """
    Recebe os bytes de um áudio, guarda-os num ficheiro temporário,
    envia para a API do Whisper da OpenAI e retorna a transcrição.
    """
    if not client:
        print("Cliente OpenAI não inicializado. Verifique a chave de API.")
        return None

    temp_audio_path = "temp_audio_file.wav"
    
    try:
        # Escreve os bytes de áudio num ficheiro temporário
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        # Abre o ficheiro temporário para leitura binária
        with open(temp_audio_path, "rb") as audio_file:
            print("A enviar áudio para a API do Whisper...")
            transcript = client.audio.transcriptions.create(
              model="whisper-1", # O modelo mais potente e rápido da OpenAI
              file=audio_file,
              language="pt"
            )
        
        texto_transcrito = transcript.text
        print(f"Texto Transcrito (via API): {texto_transcrito}")
        return texto_transcrito

    except Exception as e:
        print(f"Erro ao chamar a API do Whisper: {e}")
        return None
        
    finally:
        # Garante que o ficheiro temporário é sempre apagado
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)