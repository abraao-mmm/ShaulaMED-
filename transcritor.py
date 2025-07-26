# transcritor.py

import openai
import os

# AGORA, ele lê a chave a partir das variáveis de ambiente,
# o que funciona perfeitamente no servidor do Render.
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcrever_audio_bytes(audio_bytes):
    temp_audio_path = "temp_audio_file.wav"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
              model="whisper-1", 
              file=audio_file,
              language="pt"
            )
        
        return transcript.text
    except Exception as e:
        print(f"Erro ao chamar a API do Whisper: {e}")
        return None
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)