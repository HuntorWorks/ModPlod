from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from core.utils import mp_print
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
        self.twitch_ai_actions_manager = None
    
    async def on_ready(self, ready_event: EventData):
        mp_print.sys_message("Twitch API Manager is ready")

        await ready_event.chat.join_room(self.TWITCH_TARGET_CHANNEL)

    # Called every time someone sends a message in the chat
    async def on_message(self, message: ChatMessage):
        if self.twitch_ai_actions_manager:
            self.twitch_ai_actions_manager.process_twitch_chat(message_content=message.text, user_name=message.user.display_name)
        else:
            mp_print.error("Twitch AI Actions Manager not yet set")

#region TWITCH API MANAGER INIT AND AUTHENTICATION
    def start_twitch_api_manager(self):
        asyncio.run(self.twitch_api_manager())

    async def twitch_api_manager(self):
        mp_print.info("Starting twitch_api_manager...") 
        try:
            self.twitch = Twitch(self.client_id, self.client_secret)
            mp_print.info("Twitch instance created.")
            authenticator = UserAuthenticator(self.twitch, self.scopes, force_verify=False, url='http://localhost:17563', host='0.0.0.0', port=17563)
            mp_print.info("Authenticator created.")

            if os.path.exists("token_data.json"):
                self.load_token_data()
                self.TOKEN = self.token_data["token"]
                self.REFRESH_TOKEN = self.token_data["refresh_token"]
                self.TOKEN_EXPIRES_AT = self.token_data["expires_at"]

                if time.time() > self.TOKEN_EXPIRES_AT:
                    mp_print.info("Token expired, refreshing...")
                    await self.refresh_token()
            else:
                mp_print.warning("No token data found, performing full authentication...")
                await self.full_authentication()

            await self.twitch.set_user_authentication(self.TOKEN, self.scopes, self.REFRESH_TOKEN)

            # Create Chat Instance
            self.chat = await Chat(self.twitch)
            mp_print.info(f"Chat Instance Created: {self.chat}")

            self.register_events()

            self.chat.start()
            mp_print.info("Chat started.")
        except Exception as e:
            mp_print.error(f"Error in twitch_api_manager: {e}")
      
    async def refresh_token(self):
        try:
            new_token_data = await refresh_access_token(self.REFRESH_TOKEN, self.client_id, self.client_secret)
            self.TOKEN = new_token_data["token"]
            self.REFRESH_TOKEN = new_token_data["refresh_token"]
            self.save_token_data()
        except Exception as e:
            mp_print.error(f"Error refreshing token: {e}")
            await self.full_authentication()
        return True
    
    async def full_authentication(self):
        twitch = Twitch(self.client_id, self.client_secret)
        authenticator = UserAuthenticator(twitch, self.scopes, force_verify=False, url='http://localhost:17563', host='0.0.0.0', port=17563)
        token, refresh_token = await authenticator.authenticate()
        self.TOKEN = token
        self.REFRESH_TOKEN = refresh_token
        self.save_token_data()
#endregion
     
    async def get_broadcast_id_from_name(self, user_name: str):
        users = self.twitch.get_users(logins=[user_name])

        async for user in users:
            broadcaster_id = user.id
            return broadcaster_id
        raise Exception("No broadcaster ID found")
    
    async def send_message(self, message: str):
        try:
            await self.chat.send_message(self.TWITCH_TARGET_CHANNEL, message)
        except Exception as e:
            mp_print.error(f"Error sending message: {e} Chat Instance: {self.chat}")

    async def create_clip(self, broadcaster_id: str):
        clip_result = await self.twitch.create_clip(broadcaster_id=broadcaster_id)
        return clip_result
        
#region TOKEN MANAGEMENT
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
#endregion

#region EVENT REGISTRATION
    def register_events(self):
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
#endregion
    def set_actions_manager(self, actions_manager):
        self.twitch_ai_actions_manager = actions_manager