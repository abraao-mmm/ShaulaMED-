# transcritor.py

import whisper
import os

# Carrega o modelo do Whisper uma única vez para ser mais eficiente
model = whisper.load_model("base")

def transcrever_audio_bytes(audio_bytes):
    """
    Recebe os bytes de um áudio gravado e usa o Whisper para transcrever.
    """
    # Cria um nome de ficheiro temporário
    temp_audio_path = "temp_audio_file.wav"
    
    try:
        # Escreve os bytes de áudio num ficheiro temporário
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        print("Ficheiro de áudio temporário criado. A transcrever com o Whisper...")
        
        # Usa o Whisper para transcrever o ficheiro de áudio
        result = model.transcribe(temp_audio_path, language="pt")
        texto_transcrito = result["text"]
        
        print(f"Texto Transcrito: {texto_transcrito}")
        return texto_transcrito

    finally:
        # Garante que o ficheiro temporário é sempre apagado
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print("Ficheiro de áudio temporário apagado.")