import os
from dotenv import load_dotenv


class TwitchAIActionsManager:
    def __init__(self):
        pass

    def send_twitch_message(self, message: str):
        from core.shared_managers import twitch_api_manager
        twitch_api_manager.send_message(message)

    def send_twitch_whisper(self, user: str, message: str):
        pass

    def send_twitch_whisper_to_all(self, message: str):
        pass

    def send_twitch_ban_user(self, user: str):
        pass

    def send_twitch_unban_user(self, user: str):
        pass
    
    def process_twitch_chat(self, message: str):
        pass
    
