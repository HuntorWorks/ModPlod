from google.cloud import texttospeech
from dotenv import load_dotenv

from core.audio_manager import AudioManager
import os
import requests
import base64

class TextToSpeechManager:

    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_TTS_API_KEY")
        self.endpoint = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_api_key}"
        self.audio_manager = AudioManager()

    def sythesize_speech(self, text, voice_name, region_code, ssmlgender):
        request_speech = {
            "input": {"text": text},
            "voice": {
                "languageCode": region_code,
                "name": voice_name,
                "ssmlGender": ssmlgender,
            },
            "audioConfig": {"audioEncoding": "LINEAR16"},
        }
        
        response = requests.post(self.endpoint, json=request_speech)

        if response.status_code == 200:
            return self.decode_response_to_bytes(response.json()["audioContent"])
        else: 
            raise Exception(f"[red]ERROR[/red]: {response.status_code}, {response.text}")
        
    def decode_response_to_bytes(self, response):
        return base64.b64decode(response)

    def text_to_speech(self, text, voice_type, voice, regional_language_code):
        gender = None

        if voice_type == "male":
            gender = texttospeech.SsmlVoiceGender.MALE
        elif voice_type == "female":
            gender = texttospeech.SsmlVoiceGender.FEMALE
        else:
            gender = texttospeech.SsmlVoiceGender.NEUTRAL

        self.audio_manager.save_response_audio_to_file(self.sythesize_speech(text, voice, regional_language_code, gender))
