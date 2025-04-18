import os
import time
import datetime
from dotenv import load_dotenv
from core.utils import run_async_tasks
from core.utils import mp_print, get_str_from_args
from core.shared_managers import barry_ai_event_handler

## INFO: This class is responsible for handling the AI actions for the Twitch API. Any calls made within the code should call here.

class TwitchAIActionsManager:
    def __init__(self):
        load_dotenv()
        mp_print.info("Twitch AI Actions Manager initialized")
        self.TWITCH_TARGET_CHANNEL = os.getenv("TWITCH_TARGET_CHANNEL")

        self.command_cooldowns = {
            "clip": 10,
            "so": 10,
            "followage": 10,
            "title": 10,
            "game": 10,
            "ban": 5,
            "timeout": 5,
            "unban": 10,
        }

        self.last_command_times = {
            "clip": 0,
            "so": 0,
            "followage": 0,
            "title": 0,
            "game": 0,
            "ban": 0,
            "timeout": 0,
            "unban": 0,
        }
    def send_twitch_message(self, message: str):
        from core.shared_managers import twitch_api_manager
        
        try:
            # Directly run the coroutine without nested async function
            run_async_tasks(twitch_api_manager.send_message(message))
            mp_print.debug(f"Message sent: {message}")
        except Exception as e:
            mp_print.error(f"Error sending message: {e}")

    def generate_twitch_clip(self, user_name: str):
        from core.shared_managers import twitch_api_manager

        try:
            # Define the clip generation coroutine
            async def gen_clip():
                broadcaster_id = await twitch_api_manager.get_broadcast_id_from_name(self.TWITCH_TARGET_CHANNEL)
                clip_result = await twitch_api_manager.create_clip(broadcaster_id=broadcaster_id)
                return clip_result
            
            # Run the coroutine and get the result
            clip_result = run_async_tasks(gen_clip())
            clip_url = clip_result.edit_url.rsplit("/", 1)[0]

            
            # Process the result
            self.send_twitch_message(f"@{user_name} clipped that! Check out the clip here: {clip_url}")

        except Exception as e:
            mp_print.error(f"Error generating clip: {e}")
            self.send_twitch_message(f"Sorry @{user_name}, I couldn't generate a clip: {str(e)}")

    def send_twitch_shoutout(self, args: list, user_name: str):
        from core.shared_managers import twitch_api_manager
        if len(args) == 0:
            self.send_twitch_message(f"Sorry {user_name}, you need to specify a channel to shoutout.")
            return
        channel = args[0].replace('@', '')  # Remove @ if it's already there

        async def get_channel_info():
            broadcaster_id = await twitch_api_manager.get_broadcast_id_from_name(channel)
            channel_info = await twitch_api_manager.get_channel_info(broadcaster_id)
            return channel_info
        
        channel_info = run_async_tasks(get_channel_info())

        if channel_info is None:
            self.send_twitch_message(f"Sorry {user_name}, I couldn't find that channel.")
            return
        

        broadcaster_name = channel_info[0].broadcaster_name
        last_streamed_game = channel_info[0].game_name

        if last_streamed_game == "":
            last_streamed_game = "unknown"

        self.send_twitch_message(f"Shoutout to @{broadcaster_name}! Go and check out their channel! They were last streaming {last_streamed_game}.")

    def send_twitch_whisper(self, user: str, message: str):
        pass
    
    def send_twitch_followage(self, user_name: str, user_id: str):
        from core.shared_managers import twitch_api_manager
        try:
            async def get_followage():
                broadcaster_id = await twitch_api_manager.get_broadcast_id_from_name(self.TWITCH_TARGET_CHANNEL)   
                user = await twitch_api_manager.get_channel_followers(user_id=user_id, broadcaster_id=broadcaster_id)
                return user
            followers = run_async_tasks(get_followage())

            if followers and hasattr(followers, 'data') and len(followers.data) > 0:
                self.send_twitch_message(f"@{user_name} has been following for {self.format_duration(followers.data[0].followed_at)}!")
            else:
                self.send_twitch_message(f"@{user_name} is not following the channel.")

        except Exception as e:
            mp_print.error(f"Error getting followage: {e}")
            self.send_twitch_message(f"Sorry @{user_name}, I couldn't get your followage information.")

    def send_twitch_whisper_to_all(self, message: str):
        pass

    def send_twitch_ban_user(self, user_name: str, user_to_ban: str, reason: str):
        from core.shared_managers import twitch_api_manager
        try:
            mp_print.debug("Entering send_twitch_ban_user function")
            async def ban_user():
                is_allowed = await self.is_broadcaster_or_moderator(user_name)
                if is_allowed:
                    user_id = await twitch_api_manager.get_user_id_from_name(user_to_ban)
                    is_already_banned = await self.is_user_banned(user_id)
                    if is_already_banned:
                        self.send_twitch_message(f"User {user_to_ban} is already banned.")
                        return
                    success = await twitch_api_manager.timeout_or_ban_user(user_id, reason, timeout=False)
                    if success:
                        self.send_twitch_message(f"User {user_to_ban} was banned. Reason: {reason}")
                else:
                    self.send_twitch_message(f"Sorry, {user_name} is not a moderator of the channel.")

            run_async_tasks(ban_user())
        except Exception as e:
            mp_print.error(f"Error in send_twitch_ban_user: {e}")
            self.send_twitch_message(f"Sorry, {user_name}, there was an error banning the user.")
    
    def send_twitch_timeout_user(self, user_name: str, user_to_timeout: str, reason: str, duration: int):
        from core.shared_managers import twitch_api_manager
        try: 
            async def timeout_user():
                is_allowed = await self.is_broadcaster_or_moderator(user_name)
                if is_allowed:
                    user_id = await twitch_api_manager.get_user_id_from_name(user_to_timeout)
                    is_already_banned = await self.is_user_banned(user_id)
                    if is_already_banned:
                        return
                    success = await twitch_api_manager.timeout_or_ban_user(user_id, reason=reason, duration=duration, timeout=True)
                    if success:
                        self.send_twitch_message(f"User {user_to_timeout} was timed out for {duration} seconds. Reason: {reason}")
                else:
                    self.send_twitch_message(f"Sorry, {user_name} is not a moderator of the channel.")
            
            run_async_tasks(timeout_user())
        except Exception as e:
            mp_print.error(f"Error in send_twitch_timeout_user: {e}")
            self.send_twitch_message(f"Sorry, {user_name}, there was an error timing out the user.")

    def send_twitch_unban_user(self, user_name: str, user_to_unban: str):
        from core.shared_managers import twitch_api_manager
        try:
            async def unban_user():
                is_allowed = await self.is_broadcaster_or_moderator(user_name)
                if is_allowed:
                    user_id = await twitch_api_manager.get_user_id_from_name(user_to_unban)
                    is_banned = await self.is_user_banned(user_id)
                    if is_banned:
                        await twitch_api_manager.un_timeout_or_unban_user(user_id=user_id)
                        self.send_twitch_message(f"User {user_to_unban} was unbanned.")
                    else:
                        self.send_twitch_message(f"User {user_to_unban} is not banned.")
                else:
                    self.send_twitch_message(f"Sorry, {user_name} is not a moderator of the channel.")
            run_async_tasks(unban_user())
        except Exception as e:
            mp_print.error(f"Error in send_twitch_unban_user: {e}")
            self.send_twitch_message(f"Sorry, {user_name}, there was an error unbanning the user.")

    def set_twitch_channel_title(self, user_name: str, title: str):
        from core.shared_managers import twitch_api_manager

        try: 
            async def change_title():
                is_allowed = await self.is_broadcaster_or_moderator(user_name)
                if is_allowed:
                    await twitch_api_manager.modify_channel_title(title)
                    self.send_twitch_message(f"Channel title set to {title}.")
                else:
                    self.send_twitch_message(f"Sorry, {user_name} is not a moderator of the channel.")
            # Run the async function
            run_async_tasks(change_title())

        except Exception as e:
            mp_print.error(f"Error setting channel title: {e}")
            self.send_twitch_message(f"Sorry, I couldn't set the channel title to {title}.")

    def set_twitch_channel_game(self, user_name: str, game: str):
        from core.shared_managers import twitch_api_manager

        try: 
            async def update_game():
                is_allowed = await self.is_broadcaster_or_moderator(user_name)
                if is_allowed:
                    success = await twitch_api_manager.modify_channel_game(game)
                    
                    if success:
                        self.send_twitch_message(f"Channel game set to {game}.")
                    else:
                        self.send_twitch_message(f"Sorry, couldn't set the game to {game}. The game may not exist in Twitch's database.")

            run_async_tasks(update_game())
            
        except Exception as e:
            mp_print.error(f"Error setting channel game: {e}")
            self.send_twitch_message(f"Sorry, I couldn't set the channel game to {game}.")

    
    def days_to_readable_format(self, total_days):
        """Convert total days to readable format with years, months, and days"""
        years = total_days // 365
        remaining_days = total_days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        
        parts = []
        if years > 0:
            parts.append(f"{years} {'year' if years == 1 else 'years'}")
        if months > 0:
            parts.append(f"{months} {'month' if months == 1 else 'months'}")
        if days > 0 or (years == 0 and months == 0):
            parts.append(f"{days} {'day' if days == 1 else 'days'}")
            
        # Join with commas and 'and' for the last part
        if len(parts) > 1:
            result = ", ".join(parts[:-1]) + " and " + parts[-1]
        else:
            result = parts[0]
            
        return result
    
    def parse_timeout_command(self, args: list):
        try:
            user = args[0] # user to timeout
            duration = int(args[-1])
        except ValueError:
            raise ValueError("Invalid command format. Must be !timeout <user> <reason> <duration>")
        reason = get_str_from_args(args[1:-1])

        return user, reason, duration

    def format_duration(self, follow_date: datetime) -> str:
        follow_date = follow_date.replace(tzinfo=datetime.timezone.utc)
        current_date = datetime.datetime.now(datetime.timezone.utc)
        difference = current_date - follow_date
        return self.days_to_readable_format(difference.days)
    

    def process_twitch_chat(self, message_content: str, user_name: str, user_id: str):
        mp_print.debug(f"Processing twitch chat: {message_content}")
        if message_content.startswith("!"):
            self.process_twitch_command(message_content, user_name, user_id)
        else:
            payload = { 
                "message": message_content,
                "user_name": user_name,
                "user_id": user_id
            }
            barry_ai_event_handler.on_message_received(payload)

    def process_twitch_command(self, message_content: str, user_name: str, user_id: str):
        command = message_content.split(" ")[0].lower()
        args = message_content.split(" ")[1:]
        if command == "!clip":
            if self.can_send_command("clip"):
                self.generate_twitch_clip(user_name)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only clip once every {self.command_cooldowns['clip']} seconds.")
        if command == "!so" or command == "!shoutout":
            if self.can_send_command("so"):
                self.send_twitch_shoutout(args, user_name=None)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only shoutout once every {self.command_cooldowns['so']} seconds.")
        if command == "!followage":
            if self.can_send_command("followage"):
                self.send_twitch_followage(user_name, user_id)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only get followage once every {self.command_cooldowns['followage']} seconds.")
        if command == "!title":
            title = get_str_from_args(args)
            if self.can_send_command("title"):
                self.set_twitch_channel_title(user_name, title=title)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only change the title once every {self.command_cooldowns['title']} seconds.")
        if command == "!game":
            game = get_str_from_args(args)
            if self.can_send_command("game"):
                self.set_twitch_channel_game(user_name, game=game)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only change the game once every {self.command_cooldowns['game']} seconds.")
        if command == "!ban":
            user_to_ban = args[0]
            reason = get_str_from_args(args[1:])
            if self.can_send_command("ban"):
                self.send_twitch_ban_user(user_name, user_to_ban, reason=reason)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only ban once every {self.command_cooldowns['ban']} seconds.")
        if command == "!timeout":
            user_to_timeout, reason, duration = self.parse_timeout_command(args)
            if self.can_send_command("timeout"):
                self.send_twitch_timeout_user(user_name=user_name, user_to_timeout=user_to_timeout, reason=reason, duration=duration)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only timeout once every {self.command_cooldowns['timeout']} seconds.")
        if command == "!unban":
            user_to_unban = args[0]
            if self.can_send_command("unban"):
                self.send_twitch_unban_user(user_name=user_name, user_to_unban=user_to_unban)
            else:
                self.send_twitch_message(f"Sorry {user_name}, you can only unban once every {self.command_cooldowns['unban']} seconds.")

    async def is_broadcaster_or_moderator(self, user_name: str):
        from core.shared_managers import twitch_api_manager
        # check first if user is broadcaster
        if user_name.lower() == "beerhuntor":
            return True
        
        caster_id = await twitch_api_manager.get_broadcast_id_from_name(self.TWITCH_TARGET_CHANNEL)
        moderators = twitch_api_manager.get_channel_moderators(caster_id)

        async for mods in moderators:
            if mods.user_name.lower() == user_name.lower():
                return True
        return False

    async def is_user_banned(self, user_id: str):
        from core.shared_managers import twitch_api_manager

        caster_id = await twitch_api_manager.get_broadcast_id_from_name(self.TWITCH_TARGET_CHANNEL)
        banned_users = twitch_api_manager.get_banned_users(caster_id)  # Get the async generator directly
        async for user in banned_users:
            if user.user_id == user_id: 
                return True
        return False
    
    #FUTURE: Add per user cooldowns if it is needed.
    def can_send_command(self, command: str) -> bool: 
        now = time.time()
        last_command_time = self.last_command_times.get(command, 0)
        cooldown = self.command_cooldowns.get(command, 0)

        if now - last_command_time >= cooldown:
            self.last_command_times[command] = now
            return True
        return False