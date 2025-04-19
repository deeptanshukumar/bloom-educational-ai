import os
import tempfile
from typing import Optional
from werkzeug.datastructures import FileStorage
from google.cloud import speech
from google.cloud import texttospeech

class SpeechService:
    """Service for processing speech input"""
    
    def transcribe_audio(self, audio_file: FileStorage, language: str = "en") -> str:
        """
        Transcribe speech to text
        """
        if not audio_file:
            return ""
        client = speech.SpeechClient()
        with open(audio_file, "rb") as audio:
            audio_content = audio.read()
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language,
        )
        response = client.recognize(config=config, audio=audio)
        if response.results:
            return response.results[0].alternatives[0].transcript
        return ""
        
    
    def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech
        """
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=language, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        return response.audio_content

        """
        offline example using pyttsx3
        import pyttsx3

        def text_to_speech(self, text: str, language: str = "en") -> bytes:
            engine = pyttsx3.init()
            engine.save_to_file(text, "output.mp3")
            engine.runAndWait()
            with open("output.mp3", "rb") as audio_file:
                return audio_file.read()
        """
    