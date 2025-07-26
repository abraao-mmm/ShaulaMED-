# transcritor.py
import whisper
import os

model = whisper.load_model("base") # Usamos o modelo "base" que é rápido

def transcrever_audio_bytes(audio_bytes):
    temp_audio_path = "temp_audio_file.wav"
    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        result = model.transcribe(temp_audio_path, language="pt")
        texto_transcrito = result["text"]
        return texto_transcrito
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)