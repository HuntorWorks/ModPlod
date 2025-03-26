from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.type import AuthScope
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
    def start_twitch_api_manager(self):
        asyncio.run(self.twitch_api_manager())

    async def twitch_api_manager(self):
        twitch = await Twitch(self.client_id, self.client_secret)
        authenticator = UserAuthenticator(twitch, self.scopes, force_verify=False, url='http://localhost:17563', host='0.0.0.0', port=17563)

        if os.path.exists("token_data.json"):
            self.load_token_data()
            self.TOKEN = self.token_data["token"]
            self.REFRESH_TOKEN = self.token_data["refresh_token"]
            self.TOKEN_EXPIRES_AT = self.token_data["expires_at"]

            if time.time() > self.TOKEN_EXPIRES_AT:
                await self.refresh_token()
        else:
            # Get the token
            await self.full_authentication()

        await twitch.set_user_authentication(self.TOKEN, self.scopes, self.REFRESH_TOKEN)

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
    
    