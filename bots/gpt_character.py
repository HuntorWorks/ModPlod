from core.google_tts_manager import TextToSpeechManager
from core.openai_whisper_stt_manager import SpeechToTextManager
from core.openai_manager import OpenAIManager
from core.audio_manager import AudioManager
from core.obs_websocket_manager import OBSWebsocketManager
from core.animation_manager import AnimationManager
from core.utils import mp_print, extract_string_from_position
from core.constants import APP_MODE, Mode, Priority
from asyncio import PriorityQueue
from enum import Enum
import asyncio
import os
import tiktoken 
import time
import json

CHARACTER_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "characters.json"))

class MessageQueue(Enum) : 
        MOD = "mod"
        TEXT_TO_SPEECH = "tts"
        RAID = "raid"
        FOLLOW_SUB = "follow_sub"
        REDEEM = "redeem"
        DEFAULT = "default"
class Character:

    CONVERSATION_HISTORY_SAVE_DIR = os.path.abspath(os.path.join(os.path.join(__file__, ".."), "conversation_histories"))
    os.makedirs(CONVERSATION_HISTORY_SAVE_DIR, exist_ok=True)

    # class based managers to keep them from having multiple instances
    OPENAI_MANAGER = OpenAIManager()
    OBS_WEBSOCKET_MANAGER = OBSWebsocketManager()
    CONVERSATION_HISTORY_TOKEN_COUNT = 0
    USER_REQUEST_TOKEN_COUNT = 0
    GPT_RESPONSE_TOKEN_COUNT = 0
    CHARACTER_DATA = None



    def __init__(self, character_name, gpt_model="gpt-4o", max_tokens=150, gpt_temperature=0.7, debugging=False, event_handler=None):
        import threading 
        self.speak_lock = threading.Lock()
        self.CHARACTER_NAME = character_name
        self.chat_history_file = f"{self.CHARACTER_NAME}-ChatHistoryBackup.txt"
        self.chat_history_full_path = os.path.join(self.CONVERSATION_HISTORY_SAVE_DIR, self.chat_history_file)
        self.first_message_saved = False
        self.conversation_history = []
        self.FIRST_SYSTEM_MESSAGE = ""
        self.load_character()
        self.GPT_MODEL = gpt_model
        self.GPT_MAX_TOKENS = max_tokens
        self.GPT_TEMPERATURE = gpt_temperature
        self.CHARACTER_PERSONALITY = self.CHARACTER_DATA["personality"]
        self.CHARACTER_VOICE = self.CHARACTER_DATA["voice"]
        self.CHARACTER_VOICE_REGION_CODE = self.CHARACTER_DATA["voice_region_code"]
        self.CHARACTER_VOICE_SPEAKING_SPEED = self.CHARACTER_DATA["voice_speaking_rate"]
        mp_print.debug(f"First system message at init: {self.FIRST_SYSTEM_MESSAGE}")
        self.debugging = debugging

        # Initialise components.
        self.speech_to_text = SpeechToTextManager()
        self.audio_manager = AudioManager()
        self.text_to_speech_manager = TextToSpeechManager()
        self.event_handler = event_handler

        # Message Queue
        self.TIME_BETWEEN_MESSAGES = 5
        self.messages_in_queue = 0

        self.message_priority_queue = PriorityQueue()
        self.message_priority = { 
            Priority.HIGH: 1, # MOD, Big Donos, Subs, bits
            Priority.MEDIUM : 2, # Raids, Follows, redeems,
            Priority.LOW: 3 # Generic Chat, Chat Interaction
        }


        try:
            self.char_animation_manager = AnimationManager(self.OBS_WEBSOCKET_MANAGER, self.audio_manager, self.CHARACTER_DATA)
        except ValueError:
            mp_print.error(f"Animation manager could not be set. Character Data = {self.CHARACTER_DATA}")
    
    async def start(self):
        self.queue_task = asyncio.create_task(self.process_queue_loop())
        self.queue_task.add_done_callback(self._log_queue_crash)

    def _log_queue_crash(self, task): 
        try:
            task.result()
        except Exception as e: 
            mp_print.error(f"Queue task crashed: {e}")
            import traceback
            traceback.print_exc


    def load_character(self):

        with open(CHARACTER_JSON_PATH, "r") as file:
            json_data = json.load(file)
            self.CHARACTER_DATA = json_data["characters"][f"{self.CHARACTER_NAME}"]

        dir_name = os.path.dirname(__file__)
        full_path = os.path.join(dir_name, self.CHARACTER_DATA["first_system_message"])

        
        with open(full_path, "r") as file:
            self.FIRST_SYSTEM_MESSAGE = file.read()
            self.add_to_chat_history()

    def handle_mic_input(self, stop_recording_key):
        if not self.debugging:
            # Get mic input
            mic_text = self.speech_to_text.record_mic_input(stop_recording_key)
            if mic_text == " ":
                mp_print.error("Could not detect your input from your mic!")

            mp_print.gpt_input(mic_text)
        else:
            mic_text = "Hello there, did you know that whales have the smallest brains in the world.  And that I love grass!"

        return mic_text

    async def get_gpt_string_response(self, msg_to_respond, chat_history=True):
        if APP_MODE == Mode.DEV : 
            return "This is a fake GPT response for dev testing"
        # Get a response from GPT
        self.GPT_RESPONSE_TOKEN_COUNT = 0 # reset it from the last attempt

        if chat_history:
            content = {"role": "system", "content": self.FIRST_SYSTEM_MESSAGE}
            ai_response = await self.OPENAI_MANAGER.respond_with_chat_history_async(msg_to_respond, self.GPT_MODEL, self.GPT_TEMPERATURE,  self.GPT_MAX_TOKENS, self.conversation_history, content, True)
            split_message = extract_string_from_position(msg_to_respond, "Message:")
            mp_print.gpt_input(f"{split_message}")
        else:
            content = {"role": "system", "content": self.FIRST_SYSTEM_MESSAGE}
            ai_response = await self.OPENAI_MANAGER.respond_without_chat_history_async(msg_to_respond, self.GPT_MODEL, self.GPT_TEMPERATURE,  self.GPT_MAX_TOKENS, content, True)
            split_message = extract_string_from_position(msg_to_respond, "Message:")
            mp_print.gpt_input(f"{split_message}")

        self.GPT_RESPONSE_TOKEN_COUNT = self.get_num_tokens_per_string(ai_response)

        return ai_response
    
#FUTURE: Instead of thread locking, turn into queue system with a queue manager
    def speak(self, text):
        if APP_MODE == Mode.DEV : 
            mp_print.debug(f"[DEV] Speak Muted {text}")
            return

        with self.speak_lock:
            mp_print.ai_response(f"{text}")

            self.set_visible()
            self.text_to_speech_manager.text_to_speech(text, "male", self.CHARACTER_VOICE, self.CHARACTER_VOICE_REGION_CODE)
            time.sleep(0.1)

            self.start_text_and_jaw_animations(text)

            self.OBS_WEBSOCKET_MANAGER.clear_source_text(self.CHARACTER_DATA["obs_speech_text_source"])
            self.set_visible(False)
    
    async def add_to_queue(self, msg : str, priority : Priority) : 
        msg_reply = MessageReply(msg, priority)
        mp_print.debug(f"Prio : {msg_reply.priority.value} reply: {msg_reply.message_context}")
        await self.message_priority_queue.put((msg_reply.priority.value, msg_reply.message_context))

        # queue = self.message_queues.get(catagory.value, self.message_queues[MessageQueue.DEFAULT.value])

        # await queue.put(msg)
        self.messages_in_queue += 1
        mp_print.info(f"Messages In Queue: {self.messages_in_queue}")
        
        
    async def process_queue_loop(self) : 
        try: 
            while True : 
                if not self.message_priority_queue.empty() : 
                    msg = await self.message_priority_queue.get()
                    self.speak(msg)
                    self.messages_in_queue -= 1
                    await asyncio.sleep(self.TIME_BETWEEN_MESSAGES)
                
                await asyncio.sleep(0.1)

        except Exception as e : 
            mp_print.error("Queue Loop Crashed!")
            import traceback
            traceback.print_exc()

        

    def set_visible(self, visible=True):
        self.OBS_WEBSOCKET_MANAGER.set_source_visibility(scene=self.CHARACTER_DATA["obs_main_scene_name"], source=self.CHARACTER_DATA["obs_scene"],visibilty=visible)

    def start_text_and_jaw_animations(self, text_to_anim):
        text_anim_thread = self.char_animation_manager.animate_character_text(text_to_anim)
        audio_thread = self.audio_manager.play_character_audio()
        talk_anim_thread = self.char_animation_manager.animate_character_jaw_position()

        text_anim_thread.join()
        audio_thread.join()
        talk_anim_thread.join()

    def add_to_chat_history(self, user_msg=None, ai_response=None):
        if self.first_message_saved == False:
            self.conversation_history.append({'role': 'system', 'content': self.FIRST_SYSTEM_MESSAGE})
            self.first_message_saved = True

        if user_msg:
            self.conversation_history.append({"role": "user", "content": user_msg})
            time.sleep(0.2)
        elif ai_response:
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            time.sleep(0.2)
        else:
            mp_print.warning(f"No conversation history could be set, is it possible this is the first time this function is called?")


        with open(self.chat_history_full_path, "w") as file:
            file.write(str(self.conversation_history))

        self.CONVERSATION_HISTORY_TOKEN_COUNT += self.get_num_tokens_per_string(json.dumps(self.conversation_history))

        if self.CONVERSATION_HISTORY_TOKEN_COUNT >= self.OPENAI_MANAGER.MAX_REQUEST_TOKENS:
            self.conversation_history.pop(0)

    def get_num_tokens_per_string(self, text):
        encoding = tiktoken.encoding_for_model("gpt-4o")
        num_tokens = len(encoding.encode(text))

        return num_tokens
    


class MessageReply(): 
    def __init__(self, message_context : str, priority : Priority): 
        self.message_context = message_context
        self.priority = priority
