from google.cloud import texttospeech
from dotenv import load_dotenv

from audio_manager import AudioManager
import os
import requests
import base64

class TextToSpeechManager:

    def __init__(self, voice, region_code):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_TTS_API_KEY")
        self.endpoint = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_api_key}"
        #self.client = texttospeech.TextToSpeechClient()
        self.audio_manager = AudioManager()
        self.playback_voice = voice
        self.region_code = region_code

    def sythesize_speech(self, text, voice_name, ssmlGender):
        request_speech = {
            "input": {"text": text},
            "voice": {
                "languageCode": self.region_code,
                "name": voice_name,
                "ssmlGender": "NEUTRAL",
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

    def text_to_speech(self, text, voice_type):
        gender = None

        input = texttospeech.SynthesisInput(text=text)

        if voice_type == "male":
            gender = texttospeech.SsmlVoiceGender.MALE
        elif voice_type == "female":
            gender = texttospeech.SsmlVoiceGender.FEMALE
        else:
            gender = texttospeech.SsmlVoiceGender.NEUTRAL

        # voice_request = texttospeech.VoiceSelectionParams(
        #     language_code="en-gb",
        #     name=self.playback_voice,
        #     ssml_gender=gender,
        # )

        # audio_config = texttospeech.AudioConfig(
        #     audio_encoding=texttospeech.AudioEncoding.LINEAR16
        # )

        # response = self.client.synthesize_speech(
        #     input=input, voice=voice_request, audio_config=audio_config
        # )


        self.audio_manager.save_response_audio_to_file(self.sythesize_speech(text, self.playback_voice, gender))
