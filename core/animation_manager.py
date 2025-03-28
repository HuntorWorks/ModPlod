import time
import threading
import numpy as np

class AnimationManager():

    def __init__(self, obs_websocket_manager, audio_manager, character_data):
        self.obs_websocket_manager = obs_websocket_manager
        self.audio_manager = audio_manager
        self.character_speech_speed = character_data["voice_speaking_rate"]
        self.jaw_source_name = character_data["obs_mouth_source"]
        self.group_source_name = character_data["obs_character_group_source"]
        self.text_source_name = character_data["obs_speech_text_source"]

    def animate_character_text(self, text, delay=0.3):
        def animate_text():
            first_pass = False
            word_list = text.rsplit(' ')

            for word in word_list:
                self.obs_websocket_manager.set_source_text(self.text_source_name, word)
                time.sleep(delay)

        text_animation_thread = threading.Thread(target=animate_text, name="Text Animation Thread")
        text_animation_thread.start()
        return text_animation_thread


    def map_volume_to_jaw_pos(self, volume, min_pos=0, max_pos=50):
        return min_pos + (max_pos - min_pos) * volume

    def animate_character_jaw_position(self):
        original_transform_data = self.obs_websocket_manager.get_source_transform(
            scene_name=self.group_source_name,
            source_name=self.jaw_source_name
        )
        originalY_pos = original_transform_data.datain['sceneItemTransform']['positionY']
        def talking_animation_thread():
            volume_levels, sample_rate = self.audio_manager.get_audio_volume_levels()

            step = int(sample_rate / 10)
            for i in range(0, len(volume_levels), step):
                volume = np.mean(volume_levels[i:i + step])
                jaw_position = self.map_volume_to_jaw_pos(volume)

                self.obs_websocket_manager.set_source_transform(
                    scene_name=self.group_source_name,
                    source_name=self.jaw_source_name,
                    transform={"positionY": jaw_position}
                )

                time.sleep(self.character_speech_speed) # sync with audio.

            # reset jaw to base position.
            self.obs_websocket_manager.set_source_transform(
                scene_name=self.group_source_name,
                source_name=self.jaw_source_name,
                transform={"positionY": originalY_pos}
            )

        talking_animation_thread = threading.Thread(target=talking_animation_thread, name="Talking Animation Thread")
        talking_animation_thread.start()
        return talking_animation_thread

