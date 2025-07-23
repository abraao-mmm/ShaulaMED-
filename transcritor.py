# transcritor.py (Calibrado para Áudios Longos)

import whisper
import os

# --- AJUSTE 2 (Opcional): Usamos um modelo mais potente para maior precisão ---
# A primeira vez que rodar, ele pode precisar de descarregar este novo modelo.
model = whisper.load_model("medium")

def transcrever_audio_bytes(audio_bytes):
    """
    Recebe os bytes de um áudio gravado e usa o Whisper para transcrever.
    """
    temp_audio_path = "temp_audio_file.wav"
    
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        print("Ficheiro de áudio temporário criado. A transcrever com o Whisper...")
        
        # --- AJUSTE 1: Aumentamos o tempo máximo de processamento ---
        # A biblioteca Whisper em si não tem um limite de tempo aqui,
        # mas usar um modelo melhor ajuda a processar áudios mais longos com mais precisão.
        result = model.transcribe(temp_audio_path, language="pt")
        texto_transcrito = result["text"]
        
        print(f"Texto Transcrito: {texto_transcrito}")
        return texto_transcrito

    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print("Ficheiro de áudio temporário apagado.")