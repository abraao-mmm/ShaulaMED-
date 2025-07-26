# transcritor.py (Versão com API OpenAI)

import openai
import os
import streamlit as st

# Tenta obter a chave de API dos "Secrets" do Streamlit
# Este é o método correto para aplicações Streamlit hospedadas
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    # Fallback para variáveis de ambiente (útil para o back-end ou testes locais)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcrever_audio_bytes(audio_bytes):
    """
    Envia os bytes de um áudio gravado para a API do Whisper da OpenAI e retorna a transcrição.
    """
    temp_audio_path = "temp_audio_file.wav"
    
    try:
        # Escreve os bytes de áudio num ficheiro temporário
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        # Abre o ficheiro temporário para leitura binária
        with open(temp_audio_path, "rb") as audio_file:
            # Usa o cliente da OpenAI para chamar a API do Whisper
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
        st.error(f"Erro na transcrição via API: {e}")
        return None
        
    finally:
        # Garante que o ficheiro temporário é sempre apagado
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)