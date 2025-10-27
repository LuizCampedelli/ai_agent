import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import wave
import pyaudio
from datetime import datetime
import os

class VoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.setup_voice()

    def setup_voice(self):
        """Configura o sistema de voz"""
        # Ajusta para ruído ambiente
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Configurações da voz
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 0:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)

    def start_listening(self):
        """Inicia escuta em background"""
        self.is_listening = True
        listen_thread = threading.Thread(target=self._listen_loop)
        listen_thread.daemon = True
        listen_thread.start()

    def stop_listening(self):
        """Para a escuta"""
        self.is_listening = False

    def _listen_loop(self):
        """Loop principal de escuta"""
        while self.is_listening:
            try:
                audio_data = self.listen_once()
                if audio_data:
                    self.audio_queue.put(audio_data)
            except Exception as e:
                print(f"Erro na escuta: {e}")
            time.sleep(0.1)

    def listen_once(self, timeout=5):
        """Escuta uma única frase"""
        try:
            with self.microphone as source:
                print("🎤 Ouvindo...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            text = self.recognizer.recognize_google(audio, language='pt-BR')
            print(f"👤 Usuário disse: {text}")
            return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento: {e}")
            return None

    def speak(self, text):
        """Fala o texto fornecido"""
        def _speak():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

        # Roda em thread separada para não bloquear
        speak_thread = threading.Thread(target=_speak)
        speak_thread.daemon = True
        speak_thread.start()

    def save_audio(self, audio_data, filename=None):
        """Salva áudio para treinamento futuro"""
        if filename is None:
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # Cria diretório se não existir
        os.makedirs("audio_data", exist_ok=True)
        filepath = os.path.join("audio_data", filename)

        # Aqui você implementaria o salvamento do áudio
        # Por simplicidade, vamos apenas salvar o texto transcrito
        with open(filepath.replace('.wav', '.txt'), 'w', encoding='utf-8') as f:
            f.write(audio_data)

        return filepath

# Versão simplificada para Streamlit
class StreamlitVoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_recording = False

    def record_audio(self):
        """Grava áudio via Streamlit"""
        try:
            import streamlit as st

            audio_bytes = st.audio_input("Fale agora...", key="audio_input")

            if audio_bytes:
                # Converte bytes para AudioData do speech_recognition
                import io
                import wave

                # Salva temporariamente
                with wave.open("temp_audio.wav", 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(audio_bytes)

                # Reconhece
                with sr.AudioFile("temp_audio.wav") as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language='pt-BR')
                    return text

            return None

        except Exception as e:
            st.error(f"Erro no reconhecimento de voz: {e}")
            return None

    def text_to_speech(self, text):
        """Síntese de voz simplificada para Streamlit"""
        # Streamlit não suporta pyttsx3 diretamente, então usamos uma alternativa
        # Podemos usar uma API web ou retornar o texto para leitura visual
        return text  # Por enquanto, retorna o texto para exibição