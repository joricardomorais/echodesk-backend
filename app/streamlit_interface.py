import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
from interpretador_nlu import interpretar_comando
import requests
import os
import tempfile
import pyttsx3

st.set_page_config(page_title="EchoDesk - Atualização por Voz")
st.title("🔊 EchoDesk - Atualização de Chamados por Voz")

# Configuração global de gravação
duracao_segundos = 7
frequencia_amostragem = 16000
nome_arquivo_audio = "audio.wav"
API_URL = "https://echodesk-backend.onrender.com/chamados"  # URL base do EchoDesk

def falar_texto(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()

# Função para transcrever com Whisper (com import local)
def transcrever_audio():
    import whisper
    st.info("Carregando modelo Whisper...")
    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(nome_arquivo_audio, language="pt", task="transcribe")
    return resultado["text"]

# Função para gravar áudio
def gravar_audio():
    st.info(f"Gravando áudio por {duracao_segundos} segundos...")
    audio = sd.rec(int(duracao_segundos * frequencia_amostragem), samplerate=frequencia_amostragem, channels=1, dtype='int32')
    sd.wait()
    audio = audio / np.max(np.abs(audio))  # normaliza entre -1 e 1
    audio = (audio * 32767).astype(np.int16)  # converte para int16
    wavfile.write(nome_arquivo_audio, frequencia_amostragem, audio)
    st.success("Gravação concluída com sucesso!")

# Interface interativa
st.markdown("---")
st.header("1. Comando de Voz")

transcricao = ""
chamado_detectado = None
status_detectado = None

if st.button("🎙️ Gravar comando de voz"):
    gravar_audio()
    transcricao = transcrever_audio()
    st.write("**Transcrição:**", transcricao)

    chamado_detectado, status_detectado = interpretar_comando(transcricao)
    if chamado_detectado and status_detectado:
        st.success(f"Detectado: Chamado {chamado_detectado}, Status '{status_detectado}'")

        # Solicita confirmação por voz
        confirmacao_msg = f"Você deseja realmente atualizar o chamado {chamado_detectado} para status {status_detectado}? Por favor, diga uma frase como 'quero confirmar' ou 'pode cancelar'."
        falar_texto(confirmacao_msg)

        st.info("Aguardando resposta por voz...")
        tentativa = 0
        confirmacao = ""
        while tentativa < 2:
            gravar_audio()
            confirmacao = transcrever_audio()
            st.write(f"**Confirmação tentativa {tentativa+1}:**", confirmacao)
            if any(p in confirmacao.lower() for p in ["confirmar", "confirma", "confirmado", "quero confirmar", "pode confirmar"]):
                break
            elif any(p in confirmacao.lower() for p in ["cancelar", "não", "pode cancelar", "quero cancelar"]):
                break
            tentativa += 1

        if any(palavra in confirmacao.lower() for palavra in ["confirmar", "confirma", "confirmado", "comfirmar", "confermar"]):
            try:
                # Valida se o chamado existe
                url = f"{API_URL}/{chamado_detectado}"
                verifica = requests.get(url)
                if verifica.status_code != 200:
                    st.error(f"Chamado {chamado_detectado} não existe. A atualização foi cancelada.")
                    falar_texto(f"Chamado {chamado_detectado} não existe. Cancelando operação.")
                    raise Exception("Chamado inexistente")
                payload = {"status_atual": status_detectado}
                response = requests.put(url, json=payload)
                if response.status_code == 200:
                    st.success(f"Chamado {chamado_detectado} atualizado para '{status_detectado}' com sucesso!")
                    falar_texto(f"Chamado {chamado_detectado} atualizado com sucesso")
                else:
                    st.error(f"Erro ao atualizar chamado: {response.status_code} - {response.text}")
                    falar_texto("Houve um erro ao atualizar o chamado")
            except Exception as e:
                pass  # Suprimir mensagens de erro genéricas e falas de conexão
        elif "cancelar" in confirmacao.lower():
            st.warning("Atualização cancelada pelo usuário.")
            falar_texto("Atualização cancelada")
        else:
            st.error("Não foi possível entender a confirmação por voz.")
            falar_texto("Não foi possível entender a confirmação")

    else:
        st.warning("Não foi possível interpretar o comando.")

# Campos manuais editáveis
st.markdown("---")
st.header("2. Interpretação do Comando")

chamado = st.text_input("Chamado detectado", value=str(chamado_detectado) if chamado_detectado else "")
status = st.selectbox("Status detectado", [
    "", "Pendente", "Em andamento", "Chamado Parado", "Chamado Retomado", "Chamado Finalizado"
], index=(["", "Pendente", "Em andamento", "Chamado Parado", "Chamado Retomado", "Chamado Finalizado"].index(status_detectado) if status_detectado in ["Pendente", "Em andamento", "Chamado Parado", "Chamado Retomado", "Chamado Finalizado"] else 0))