## Handles all audio processes... deletion of recordings... recording audio etc
import os

PROJECT_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RECORDINGS_PATH = os.path.join(PROJECT_ROOT_PATH, "recordings")

import numpy as np
import sounddevice as sd
import soundfile as sf
from core.utils import mp_print

import threading


class AudioManager():
    def __init__(self):
        self.audio_buffer = []
        self.audio_chunk_list = {}
        self.mic_rec_audio_filename = os.path.join(RECORDINGS_PATH, "mic_recording.wav")
        self.response_audio_filename = os.path.join(RECORDINGS_PATH, "gpt_response.wav")

    def mic_input_callback(self, indata, frames, time, status):
        if status:
            mp_print.warning(f"{status}")
        self.audio_buffer.append(indata.copy())

    def save_mic_audio_to_file(self, sample_rate):
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        sf.write(self.mic_rec_audio_filename, audio_data, sample_rate)
        self.audio_buffer = []

    def save_response_audio_to_file(self, audio_content):
        with open(self.response_audio_filename, "wb") as out:
            out.write(audio_content)

    def play_character_audio(self):
        def play_audio():
            data, samplerate = sf.read(self.response_audio_filename)
            sd.play(data, samplerate)
            sd.wait()

        audio_thread = threading.Thread(target=play_audio, name="Play Audio Thread")
        audio_thread.start()
        return audio_thread

    def get_audio_volume_levels(self):
        data, sample_rate = sf.read(self.response_audio_filename)
        volume_levels = np.abs(data)
        return volume_levels, sample_rate