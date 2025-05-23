from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token, validate_token
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from core.utils import mp_print
from core.constants import NGROK_DEV_TUNNEL_URL, NGROK_LIVE_TUNNEL_URL, APP_MODE, Mode
import requests
from dotenv import load_dotenv
import time, os, json, asyncio

#
class TwitchAPIManager:

    def __init__(self):
        load_dotenv()

        # Twitch Bot Client ID and Secret
        self.bot_client_id = os.getenv("TWITCH_CLIENT_ID_BOT")
        self.bot_client_secret = os.getenv("TWITCH_CLIENT_SECRET_BOT")

        # Twitch Broadcaster Client ID and Secret
        self.broadcaster_client_id = os.getenv("TWITCH_CLIENT_ID_BROADCASTER")
        self.broadcaster_client_secret = os.getenv("TWITCH_CLIENT_SECRET_BROADCASTER")

        self.scopes_bot = [
            AuthScope.CHAT_READ, 
            AuthScope.CHAT_EDIT, 
            AuthScope.MODERATOR_MANAGE_BANNED_USERS,
            AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
            AuthScope.MODERATOR_READ_MODERATORS, 
            AuthScope.CLIPS_EDIT,
            AuthScope.MODERATOR_READ_FOLLOWERS,
            AuthScope.MODERATION_READ, 
            AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
            AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS,
            AuthScope.MODERATOR_MANAGE_AUTOMOD,
            AuthScope.MODERATOR_MANAGE_SHOUTOUTS,
            AuthScope.CHANNEL_MANAGE_VIPS,
            AuthScope.WHISPERS_READ,
            AuthScope.WHISPERS_EDIT
        ]
        
        self.scopes_broadcaster = [
            AuthScope.CHANNEL_MANAGE_VIDEOS,
            AuthScope.CHANNEL_MANAGE_BROADCAST, 
            AuthScope.MODERATION_READ,
            AuthScope.MODERATOR_MANAGE_BANNED_USERS,
            AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
            AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
            AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS,
            AuthScope.MODERATOR_MANAGE_AUTOMOD,
            AuthScope.MODERATOR_MANAGE_SHOUTOUTS,
            AuthScope.CHANNEL_MANAGE_VIPS,
            AuthScope.CHANNEL_READ_SUBSCRIPTIONS
            
        ]
        
        self.twitch_bot = None
        self.twitch_broadcaster = None
        self.twitch_chat = None
        self.token_data_bot = None
        self.token_data_broadcaster = None
        self.is_bot_authenticated = False
        self.twitch_bot_display_name = None
        
        self.twitch_ai_actions_manager = None
        self.TWITCH_TARGET_CHANNEL = os.getenv("TWITCH_TARGET_CHANNEL")

        self.NGROK_URL = NGROK_LIVE_TUNNEL_URL if APP_MODE == Mode.LIVE else NGROK_DEV_TUNNEL_URL
    
    async def on_ready(self, ready_event: EventData):
        mp_print.sys_message("Twitch API Manager is ready")

        await ready_event.chat.join_room(self.TWITCH_TARGET_CHANNEL)

    # Called every time someone sends a message in the chat
    async def on_message(self, message: ChatMessage):
        if message.user.display_name == self.twitch_bot_display_name:
            mp_print.debug("Ignoring message sent by the bot itself.")
            return
        if self.twitch_ai_actions_manager:
            self.twitch_ai_actions_manager.process_twitch_chat(message_content=message.text, user_name=message.user.display_name, user_id=message.user.id)
        else:
            mp_print.warning("Twitch AI Actions Manager not yet set")

#region TWITCH API MANAGER INIT AND AUTHENTICATION
    def start_twitch_api_manager(self):
        asyncio.create_task(self.twitch_api_manager())
    
    async def authenticate_broadcaster(self):
        try:
            self.twitch_broadcaster = Twitch(self.broadcaster_client_id, self.broadcaster_client_secret)
            await self.load_or_authenticate(self.twitch_broadcaster, "broadcaster_token_data.json", self.scopes_broadcaster)
            user = self.twitch_broadcaster.get_users()
            async for u in user:
                self.broadcaster_id = u.id
        except Exception as e:
            mp_print.error(f"Error authenticating twitch_broadcaster: {e}")
            
    async def authenticate_bot(self):
        try: 
            self.twitch_bot = Twitch(self.bot_client_id, self.bot_client_secret)
            self.token_data_bot = await self.load_or_authenticate(self.twitch_bot, "bot_token_data.json", self.scopes_bot)

            # Mark as authenticated if token exists
            if self.token_data_bot:
                self.is_bot_authenticated = True
                #mp_print.info(f"Bot token data assigned: {self.token_data_bot}")

            # Validate user info after token is applied
            user_info = self.twitch_bot.get_users()
            async for u in user_info:
                self.twitch_bot_user_id = u.id
                self.twitch_bot_display_name = u.display_name

        except Exception as e:
            mp_print.error(f"Error authenticating twitch_bot: {e}")


    async def load_or_authenticate(self, twitch_instance, token_file, scopes): 
        token_data = None
        if os.path.exists(token_file):
            token_data = self.load_token_data(token_file)

            if time.time() > token_data["expires_at"]:
                mp_print.info("Token expired, refreshing...")
                await self.refresh_token(token_file)
                token_data = self.load_token_data(token_file)  # reload new token

            await twitch_instance.set_user_authentication(token_data["token"], scopes, token_data["refresh_token"])
            return token_data

        else:
            auth = UserAuthenticator(twitch_instance, scopes, force_verify=True, url="http://localhost:17563", host="0.0.0.0", port=17563)
            token, refresh_token = await auth.authenticate()
            self.save_token_data(token_file, token, refresh_token)
            token_data = self.load_token_data(token_file)
            await twitch_instance.set_user_authentication(token, scopes, refresh_token)

        return token_data


    async def twitch_api_manager(self):
        mp_print.info("Starting twitch_api_manager...") 
        try: 
            await self.authenticate_bot()
            await self.authenticate_broadcaster()
            mp_print.info("Twitch API Manager Authenticated")
            # Unsubscribe from all eventSubs
            mp_print.debug("Unsubscribing from all previouseventSubs")
            await self.unsubscribe_all_eventsub()

            # Subscribe to eventSubs
            mp_print.debug("Subscribing to eventSubs")
            await self.subscribe_to_eventsub_subscribe()
            await self.subscribe_to_eventsub_subscribe_gift()
            await self.subscribe_to_eventsub_subscription_msg()
            await self.subscribe_to_eventsub_follow()
            await self.subscribe_to_eventsub_raid()

            # Create Chat Instance
            self.chat = await Chat(self.twitch_bot)
            self.register_events()
            self.chat.start()
        except Exception as e:
            mp_print.error(f"Error in twitch_api_manager: {e}")
      
    async def refresh_token(self, token_file):
        try:
            token_data = self.load_token_data(token_file)

            if "bot" in token_file:
                client_id = self.bot_client_id
                client_secret = self.bot_client_secret
            elif "broadcaster" in token_file:
                client_id = self.broadcaster_client_id
                client_secret = self.broadcaster_client_secret
            else:
                raise ValueError("Unknown token type in file name")

            new_token, new_refresh_token = await refresh_access_token(token_data["refresh_token"], client_id, client_secret)
            
            
            self.save_token_data(token_file, new_token, new_refresh_token)
        
        except Exception as e:
            mp_print.error(f"Error refreshing token: {e}")

            if "bot" in token_file:
                await self.authenticate_bot()
            elif "broadcaster" in token_file:
                await self.authenticate_broadcaster()
                
        return True  
#endregion

#region SHARED API Calls
    async def get_channel_info(self, broadcaster_id: str):
        channel_info = await self.twitch_bot.get_channel_information(broadcaster_id)
        return channel_info
    
    async def get_broadcast_id_from_name(self, user_name: str):
        users = self.twitch_bot.get_users(logins=[user_name])

        async for user in users:
            broadcaster_id = user.id
            return broadcaster_id
        raise Exception("No broadcaster ID found")
    
    async def get_user_id_from_name(self, user_name: str):
        users = self.twitch_bot.get_users(logins=[user_name])

        async for user in users:
            user_id = user.id
            return user_id
        
        raise Exception("No user ID found")
    
    async def get_channel_followers(self, broadcaster_id: str, user_id: None):
        mp_print.debug(f"Broadcaster ID: {broadcaster_id}, User ID: {user_id}")
        followers = await self.twitch_bot.get_channel_followers(broadcaster_id=broadcaster_id, user_id=user_id)
        return followers
    
    def get_channel_moderators(self, broadcaster_id: str):
        moderators = self.twitch_broadcaster.get_moderators(broadcaster_id=broadcaster_id)
        return moderators
    
    async def send_message(self, message: str):
        try:
            await self.chat.send_message(self.TWITCH_TARGET_CHANNEL, message)
        except Exception as e:
            mp_print.error(f"Error sending message: {e} Chat Instance: {self.chat}")

    async def create_clip(self, broadcaster_id: str):
        clip_result = await self.twitch_bot.create_clip(broadcaster_id=broadcaster_id)
        return clip_result
    
    async def get_game_id_by_name(self, game_name: str):
        games_async_gen = self.twitch_bot.get_games(names=[game_name])
        async for game in games_async_gen:
            return game.id
        mp_print.error(f"Could not find game ID for: {game_name}")
        return None
    
    async def timeout_or_ban_user(self, user_id: str, reason = None, duration = 600, timeout = True):
        try:
            if timeout:
                if reason == None:
                    reason = "No reason provided"
                await self.twitch_bot.ban_user(broadcaster_id=self.broadcaster_id, moderator_id=self.twitch_bot_user_id, user_id=user_id, reason=reason, duration=duration)
                return True
            else:
                duration = None
                if reason == None:
                    reason = "No reason provided"
                await self.twitch_bot.ban_user(broadcaster_id=self.broadcaster_id, moderator_id=self.twitch_bot_user_id, user_id=user_id, reason=reason, duration=duration)
                return True
        except Exception as e:
            mp_print.error(f"Error banning or timing out user: {e}")
            return False
        
    def get_banned_users(self, broadcaster_id: str):
        return self.twitch_broadcaster.get_banned_users(broadcaster_id=broadcaster_id)
        
        
    
    # NOTE: Should we consider if unbanning or untiming out a user is needed to be done via barry_ai, or should it be done broadcaster side manually?
    async def un_timeout_or_unban_user(self, user_id: str):
        try:
            await self.twitch_bot.unban_user(broadcaster_id=self.broadcaster_id, moderator_id=self.twitch_bot_user_id, user_id=user_id)
        except Exception as e:
            mp_print.error(f"Error unbanning or untiming out user: {e}")
            return False
#endregion

#region BROADCASTER API CALLS
    async def modify_channel_title(self, title: str):
        try:
            # Use the broadcaster's ID that was stored during authentication
            # No need to fetch it again since we already have it
            await self.twitch_broadcaster.modify_channel_information(broadcaster_id=str(self.broadcaster_id), title=title)
            mp_print.info(f"Title successfully set to: {title}")
        except Exception as e:
            mp_print.error(f"Twitch API Exception: {e}")

    async def modify_channel_game(self, game_name: str):
        """Set the channel's game using the game name"""
        try:
            game_id = await self.get_game_id_by_name(game_name)
            # Use the broadcaster's ID that was stored during authentication
            await self.twitch_broadcaster.modify_channel_information(broadcaster_id=str(self.broadcaster_id), game_id=game_id)
            mp_print.info(f"Game successfully set to: {game_name}")
            return True
        except Exception as e:
            mp_print.error(f"Twitch API Exception: {e}")
            return False
#endregion
#region TOKEN MANAGEMENT
    def save_token_data(self, token_file, token, refresh_token):
        expires_at = time.time() + 3600 # 1 hour standard for oauth tokens
        with open(token_file, "w") as f:
            json.dump({"token": token, "refresh_token": refresh_token, "expires_at": expires_at}, f)
            
    def load_token_data(self, token_file : str) -> dict:
        with open(token_file, "r") as f:
            data = json.load(f)
            return data  
#endregion

#region CHAT EVENT REGISTRATION
    def register_events(self):
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
#endregion
    def set_actions_manager(self, actions_manager):
        self.twitch_ai_actions_manager = actions_manager

# EVENTSUBS
    async def subscribe_to_eventsub_follow(self):
        if not self.is_bot_authenticated or not self.token_data_bot:
            mp_print.error("No token data found. Did you authenticate?")
            return False
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        app_token = await self.get_broadcaster_access_token()
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "channel.follow",
            "version": "2",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id,
                "moderator_user_id" : self.broadcaster_id
            },
            "transport": {
                "method": "webhook",
                "callback": f"{self.NGROK_URL}/twitch/eventsub/callback/follow",
                "secret": "modplod-secret"
            }
        }

        response = requests.post(event_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 409 and "subscription already exists" in str(response_data):
            mp_print.info("Follow event subscription already exists")
            return True
        elif response.status_code == 202:
            mp_print.info("Successfully subscribed to follow events")
            return True
        else:
            mp_print.error(f"Error subscribing to follow events: {response_data}")
            return False
    
    async def subscribe_to_eventsub_subscribe(self):
        if not self.is_bot_authenticated or not self.token_data_bot:
            mp_print.error("No token data found. Did you authenticate?")
            return False
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        app_token = await self.get_broadcaster_access_token()
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "channel.subscribe",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id
            },
            "transport": {
                "method": "webhook",
                "callback": f"{self.NGROK_URL}/twitch/eventsub/callback/subscribe",
                "secret": "modplod-secret"
            }
        }

        response = requests.post(event_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 409 and "subscription already exists" in str(response_data):
            mp_print.info("Subscribe event subscription already exists")
            return True
        elif response.status_code == 202:
            mp_print.info("Successfully subscribed to subscribe events")
            return True
        else:
            mp_print.error(f"Error subscribing to subscribe events: {response_data}")
            return False

    async def subscribe_to_eventsub_subscribe_gift(self):
        if not self.is_bot_authenticated or not self.token_data_bot:
            mp_print.error("No token data found. Did you authenticate?")
            return False
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        app_token = await self.get_broadcaster_access_token()
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "channel.subscription.gift",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id
            }, 
            "transport": {
                "method": "webhook",
                "callback": f"{self.NGROK_URL}/twitch/eventsub/callback/subscribe_gift",
                "secret": "modplod-secret"
            }
        }

        response = requests.post(event_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 409 and "subscription already exists" in str(response_data):
            mp_print.info("Subscribe gift event subscription already exists")
            return True
        elif response.status_code == 202:
            mp_print.info("Successfully subscribed to subscribe gift events")
            return True
        else:
            mp_print.error(f"Error subscribing to subscribe gift events: {response_data}")
            return False
    
    async def subscribe_to_eventsub_subscription_msg(self):
        if not self.is_bot_authenticated or not self.token_data_bot:
            mp_print.error("No token data found. Did you authenticate?")
            return False
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        app_token = await self.get_broadcaster_access_token()
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {app_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "channel.subscription.message",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id
            }, 
            "transport": {
                "method": "webhook",
                "callback": f"{self.NGROK_URL}/twitch/eventsub/callback/subscription_msg",
                "secret": "modplod-secret"
            }
        }

        response = requests.post(event_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 409 and "subscription already exists" in str(response_data):
            mp_print.info("Subscription message event subscription already exists")
            return True
        elif response.status_code == 202:
            mp_print.info("Successfully subscribed to subscription message events")
            return True
        else:
            mp_print.error(f"Error subscribing to subscription message events: {response_data}")
            return False

    async def subscribe_to_eventsub_raid(self):
        if not self.is_bot_authenticated or not self.token_data_bot:
            mp_print.error("No token data found. Did you authenticate?")
            return False
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        app_token = await self.get_broadcaster_access_token()
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {await self.get_broadcaster_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "channel.raid",
            "version": "1",
            "condition": {
                "to_broadcaster_user_id": self.broadcaster_id
            }, 
            "transport": {
                "method": "webhook",
                "callback": f"{self.NGROK_URL}/twitch/eventsub/callback/incoming_raid",
                "secret": "modplod-secret"
            }
        }

        response = requests.post(event_url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 409 and "subscription already exists" in str(response_data):
            mp_print.info("Incoming raid event subscription already exists")
            return True
        elif response.status_code == 202:
            mp_print.info("Successfully subscribed to incoming raid events")
            return True
        else:
            mp_print.error(f"Error subscribing to incoming raid events: {response_data}")
            return False

    
    async def unsubscribe_all_eventsub(self):
        event_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        headers = {
            "Client-ID": self.broadcaster_client_id,
            "Authorization": f"Bearer {await self.get_broadcaster_access_token()}",
            "Content-Type": "application/json"
        }
        
        get_response = requests.get(event_url, headers=headers)
        subscriptions = get_response.json()
        
        if "data" not in subscriptions or not subscriptions["data"]:
            mp_print.info("No active eventSubs found to unsubscribe from")
            return True
            
        for sub in subscriptions["data"]:
            sub_id = sub.get("id")
            if sub_id:
                delete_response = requests.delete(f"{event_url}?id={sub_id}", headers=headers)
                if delete_response.status_code == 204:
                    mp_print.info(f"Successfully unsubscribed from eventSub: {sub_id}")
                else:
                    mp_print.error(f"Failed to unsubscribe from eventSub {sub_id}: {delete_response.json()}")
        
        mp_print.info(f"Unsubscribed from {len(subscriptions['data'])} eventSubs")
        return True
    
    async def get_app_access_token(self):
        await self.twitch_bot.authenticate_app([])
        app_token = self.twitch_bot.get_app_token()
        return app_token
    
    async def get_broadcaster_access_token(self):
        await self.twitch_broadcaster.authenticate_app([])
        broadcaster_token = self.twitch_broadcaster.get_app_token()
        return broadcaster_token
    