import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import whisper

# Configurações de gravação
duracao_segundos = 5  # Tempo de gravação
frequencia_amostragem = 16000  # Taxa de amostragem para Whisper

def gravar_audio(nome_arquivo):
    print(f"Gravando áudio por {duracao_segundos} segundos...")
    audio = sd.rec(int(duracao_segundos * frequencia_amostragem), samplerate=frequencia_amostragem, channels=1, dtype='int16')
    sd.wait()
    wavfile.write(nome_arquivo, frequencia_amostragem, audio)
    print("Gravação finalizada!")

def transcrever_audio(nome_arquivo):
    print("Carregando modelo Whisper...")
    modelo = whisper.load_model("small")  # Pode mudar para 'base', 'medium', etc.
    print("Transcrevendo o áudio...")
    resultado = modelo.transcribe(nome_arquivo, language="portuguese")
    print("\nTexto transcrito:")
    print(resultado["text"])

if __name__ == "__main__":
    nome_arquivo = "audio.wav"
    gravar_audio(nome_arquivo)
    transcrever_audio(nome_arquivo)
