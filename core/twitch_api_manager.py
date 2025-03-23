import os
import json
import time
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import EventData, ChatMessage, Chat
import asyncio
import threading 
from dotenv import load_dotenv


class TwitchAPIManager:
    def __init__(self):
        load_dotenv()
        self.APP_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
        self.APP_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
        self.USER_SCOPE = [
            AuthScope.CHAT_READ,
            AuthScope.CHANNEL_MODERATE,
            AuthScope.MODERATOR_MANAGE_BANNED_USERS,
            AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
        ]
        print(f"running api manager")

    def start_twitch_api_manager(self):
        thread = threading.Thread(target=self.run).start()
        thread.start()

    async def on_ready(self, ready_event: EventData):
        print("Ready to join channels")

        await ready_event.chat.join_room(os.getenv("TWITCH_TARGET_CHANNEL"))

    async def on_message(self, msg: ChatMessage):
        print(f"{msg.room.name}, {msg.user.name}, said: {msg.text}")

    def save_token(self, token_data):
        try: 
            with open("token.json", "w") as file:
                json.dump(token_data, file)
        except Exception as e:
            print(f"Failed to save token: {e}")

    def load_token(self):
        try: 
            with open("token.json", "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load token: {e}")
            return None

    async def run(self):
        twitch = await Twitch(self.APP_CLIENT_ID, self.APP_CLIENT_SECRET)
        auth = UserAuthenticator(twitch, self.USER_SCOPE)

        token = None
        refresh_token = None

        token_data = self.load_token()


        if token_data: 
            token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]

            if token_data["expires_at"] < time.time():
                print(f"Token expired, refreshing token..")
                try: 
                    new_token_data = await twitch.get_refreshed_user_auth_token(refresh_token)
                    token = new_token_data["access_token"]
                    refresh_token = new_token_data["refresh_token"]
                    self.save_token(new_token_data)
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    token, refresh_token = None, None
            else: 
                print(f"Using saved token")

        if not token or not refresh_token:
            token, refresh_token = await auth.authenticate()
            self.save_token({"access_token": token, "refresh_token": refresh_token, "expires_at": time.time() + 3600})


        await twitch.set_user_authentication(token, self.USER_SCOPE, refresh_token)

        # Creates Chat Instance
        chat = await Chat(twitch)

        # Listen to when the bot is done starting up and ready to join channels
        chat.register_event(ChatEvent.READY, self.on_ready)
        # Listen to chat messages
        chat.register_event(ChatEvent.MESSAGE, self.on_message)

        chat.start()

        try:
            input("press ENTER to stop\n")
        finally:
            chat.stop()
            await twitch.close()

