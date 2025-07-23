# transcritor.py (Calibrado para Melhor Performance)

import speech_recognition as sr
import time

def ouvir_e_transcrever(timeout_seconds=60):
    """
    Ativa o microfone, ouve a fala do usuário, e usa o Whisper para transcrever.
    Versão calibrada para maior precisão e tempo de fala.
    """
    # Inicializa o reconhecedor de fala
    r = sr.Recognizer()
    
    # --- AJUSTE 1: Aumentamos o limiar de pausa ---
    # Agora, o sistema espera 1.5 segundos de silêncio antes de considerar
    # que a frase terminou. O padrão é 0.8s.
    r.pause_threshold = 1.5
    
    with sr.Microphone() as source:
        print("\nOuvindo a fala do paciente... Fale agora.")
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # --- AJUSTE 2: Aumentamos o tempo máximo da frase ---
            # Agora o usuário pode falar por até 30 segundos continuamente.
            audio = r.listen(source, timeout=timeout_seconds, phrase_time_limit=30)
            
            print("Áudio capturado. Processando com o Whisper (modelo 'small')...")
            
            # --- AJUSTE 3: Usamos um modelo mais potente ---
            # Trocamos "base" por "small". A primeira vez que rodar,
            # ele pode demorar um pouco para descarregar o novo modelo.
            texto_transcrito = r.recognize_whisper(audio, model="small", language="portuguese")
            
            print(f"Texto Transcrito: {texto_transcrito}")
            return texto_transcrito
            
        except sr.WaitTimeoutError:
            print("Timeout: Nenhuma fala detectada.")
            return None
        except sr.UnknownValueError:
            print("Whisper não conseguiu entender o áudio.")
            return None
        except sr.RequestError as e:
            print(f"Erro no serviço do Whisper; {e}")
            return None

if __name__ == '__main__':
    texto = ouvir_e_transcrever()
    if texto:
        print(f"\nResultado final da transcrição: {texto}")