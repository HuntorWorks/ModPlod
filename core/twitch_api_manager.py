from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from dotenv import load_dotenv
import time, os, json, asyncio

#
class TwitchAPIManager:

    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.scopes = [
            AuthScope.CHAT_READ, 
            AuthScope.CHAT_EDIT, 
            AuthScope.MODERATOR_MANAGE_BANNED_USERS,
            AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
            AuthScope.MODERATOR_READ_MODERATORS, 
            AuthScope.CLIPS_EDIT,
            AuthScope.MODERATOR_READ_FOLLOWERS, 
            AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
            AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS,
            AuthScope.MODERATOR_MANAGE_AUTOMOD,
            AuthScope.MODERATOR_MANAGE_SHOUTOUTS,
            AuthScope.CHANNEL_MANAGE_VIPS,
            AuthScope.WHISPERS_READ,
            AuthScope.WHISPERS_EDIT 
            ]
        self.token_data = None
        self.TOKEN = None
        self.REFRESH_TOKEN = None 
        self.TWITCH_TARGET_CHANNEL = os.getenv("TWITCH_TARGET_CHANNEL")

        self.chat = None
    
    async def on_ready(self, ready_event: EventData):
        print("Twitch API Manager is ready")

        await ready_event.chat.join_room(self.TWITCH_TARGET_CHANNEL)

    async def on_message(self, message: ChatMessage):
        try: 
            print(f"Message received: {message.user.display_name}: {message.text}")

            if message.text == "!test":
                await message.chat.send_message(self.TWITCH_TARGET_CHANNEL, "Hello, world!")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def start_twitch_api_manager(self):
        asyncio.run(self.twitch_api_manager())

    async def twitch_api_manager(self):
        print("Starting twitch_api_manager...")
        try:
            twitch = await Twitch(self.client_id, self.client_secret)
            print("Twitch instance created.")
            authenticator = UserAuthenticator(twitch, self.scopes, force_verify=False, url='http://localhost:17563', host='0.0.0.0', port=17563)
            print("Authenticator created.")

            if os.path.exists("token_data.json"):
                self.load_token_data()
                self.TOKEN = self.token_data["token"]
                self.REFRESH_TOKEN = self.token_data["refresh_token"]
                self.TOKEN_EXPIRES_AT = self.token_data["expires_at"]

                if time.time() > self.TOKEN_EXPIRES_AT:
                    print("Token expired, refreshing...")
                    await self.refresh_token()
            else:
                print("No token data found, performing full authentication...")
                await self.full_authentication()

            await twitch.set_user_authentication(self.TOKEN, self.scopes, self.REFRESH_TOKEN)
            print("User authentication set.")

            # Create Chat Instance
            self.chat = await Chat(twitch)
            print(f"Chat Instance Created: {self.chat}")

            self.register_events()

            self.chat.start()
            print("Chat started.")
        except Exception as e:
            print(f"Error in twitch_api_manager: {e}")
      
    async def refresh_token(self):
        try:
            new_token_data = await refresh_access_token(self.REFRESH_TOKEN, self.client_id, self.client_secret)
            self.TOKEN = new_token_data["token"]
            self.REFRESH_TOKEN = new_token_data["refresh_token"]
            self.save_token_data()
        except Exception as e:
            print(f"Error refreshing token: {e}")
            await self.full_authentication()
        return True
    
    async def full_authentication(self):
        twitch = await Twitch(self.client_id, self.client_secret)
        authenticator = UserAuthenticator(twitch, self.scopes, force_verify=False, url='http://localhost:17563', host='0.0.0.0', port=17563)
        token, refresh_token = await authenticator.authenticate()
        self.TOKEN = token
        self.REFRESH_TOKEN = refresh_token
        self.save_token_data()

    async def send_message(self, message: str):
        print(f"Sending message: {message} to {self.TWITCH_TARGET_CHANNEL}")
        try:
            await self.chat.send_message(self.TWITCH_TARGET_CHANNEL, message)
        except Exception as e:
            print(f"Error sending message: {e} Chat Instance: {self.chat}")

    async def send_whisper(self, user: str, message: str):
        await self.chat.send_whisper(user, message)

    async def send_whisper_to_all(self, message: str):
        await self.chat.send_whisper_to_all(message)

    async def ban_user(self, user: str):
        await self.chat.ban_user(self.TWITCH_TARGET_CHANNEL, user)

    async def unban_user(self, user: str):
        await self.chat.unban_user(self.TWITCH_TARGET_CHANNEL, user)
        
    async def timeout_user(self, user: str, duration: int):
        await self.chat.timeout_user(self.TWITCH_TARGET_CHANNEL, user, duration)

    async def untimeout_user(self, user: str):
        await self.chat.untimeout_user(self.TWITCH_TARGET_CHANNEL, user)
    
    async def add_blocked_term(self, term: str):
        await self.chat.add_blocked_term(self.TWITCH_TARGET_CHANNEL, term)

    async def remove_blocked_term(self, term: str):
        await self.chat.remove_blocked_term(self.TWITCH_TARGET_CHANNEL, term)
        
    async def create_clip(self, title: str):
        await self.chat.create_clip(self.TWITCH_TARGET_CHANNEL, title)

    async def create_clip_with_vod(self, title: str, vod_id: str):
        await self.chat.create_clip_with_vod(self.TWITCH_TARGET_CHANNEL, title, vod_id)
        
    async def delete_clip(self, clip_id: str):
        await self.chat.delete_clip(self.TWITCH_TARGET_CHANNEL, clip_id)

    async def delete_clip_with_vod(self, clip_id: str, vod_id: str):
        await self.chat.delete_clip_with_vod(self.TWITCH_TARGET_CHANNEL, clip_id, vod_id)
        
    async def get_clip(self, clip_id: str):
        return await self.chat.get_clip(self.TWITCH_TARGET_CHANNEL, clip_id)

    async def get_clip_with_vod(self, clip_id: str, vod_id: str):
        return await self.chat.get_clip_with_vod(self.TWITCH_TARGET_CHANNEL, clip_id, vod_id)
        

    def save_token_data(self):
        expires_at = time.time() + 3600 # 1 hour standard for oauth tokens
        with open("token_data.json", "w") as f:
            json.dump({"token": self.TOKEN, "refresh_token": self.REFRESH_TOKEN, "expires_at": expires_at}, f)
            self.TOKEN_EXPIRES_AT = expires_at

    def load_token_data(self):
        with open("token_data.json", "r") as f:
            data = json.load(f)
            self.token_data = data
    
    def get_token(self):
        return self.TOKEN

    def get_refresh_token(self):
        return self.REFRESH_TOKEN
    

    def register_events(self):
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
