## Takes mic input and returns what was said to text and sends to audio_manager to delete
import time

import sounddevice as sd
from core.audio_manager import AudioManager
from rich import print
import numpy as np
import keyboard
import os
import whisper


class SpeechToTextManager:
    def __init__(self, stop_recording_keybind=None, sample_rate=48000,): #  TODO: Change this keybind
        self.audio_manager = AudioManager()
        self.stop_recording_keybind = stop_recording_keybind
        self.sample_rate = sample_rate
        self.model = whisper.load_model("small")

    def record_mic_input(self):
        buffer = []
        with sd.InputStream(callback=self.audio_manager.mic_input_callback):
            print("[bold red]Recording... ")
            while not keyboard.is_pressed(self.stop_recording_keybind):
                time.sleep(0.1)

        self.audio_manager.save_mic_audio_to_file(self.sample_rate)
        return self.get_text_from_speech()

    def get_text_from_speech(self):
        abs_path = os.path.abspath(self.audio_manager.mic_rec_audio_filename)

        if not os.path.exists(abs_path):
            raise FileNotFoundError (f"[bold red]ERROR[/bold red][white]:File not found:[/white][yellow]{abs_path}")

        transcription_dict = self.model.transcribe(abs_path)

        for key, value, in transcription_dict.items():
            if key == "text":
                return value
            else:
                print(f"[bold red]ERROR:[/bold red][white]No text could be found from recording[/white][yellow]{abs_path}")










