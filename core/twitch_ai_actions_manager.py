import os
import time
from dotenv import load_dotenv
from core.utils import run_async_tasks
from core.utils import mp_print

## INFO: This class is responsible for handling the AI actions for the Twitch API. Any calls made within the code should call here.

class TwitchAIActionsManager:
    def __init__(self):
        load_dotenv()
        mp_print.info("Twitch AI Actions Manager initialized")
        self.TWITCH_TARGET_CHANNEL = os.getenv("TWITCH_TARGET_CHANNEL")

        self.COMMAND_COOLDOWN = 10
        self.last_clip_time = 0  # Initialize last_clip_time

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

        if last_streamed_game is "":
            last_streamed_game = "unknown"

        self.send_twitch_message(f"Shoutout to @{broadcaster_name}! Go and check out their channel! They were last streaming {last_streamed_game}.")

    def send_twitch_whisper(self, user: str, message: str):
        pass

    def send_twitch_whisper_to_all(self, message: str):
        pass

    def send_twitch_ban_user(self, user: str):
        pass

    def send_twitch_unban_user(self, user: str):
        pass
    
    def process_twitch_chat(self, message_content: str, user_name: str):
        mp_print.debug(f"Processing twitch chat: {message_content}")
        if message_content.startswith("!"):
            self.process_twitch_command(message_content, user_name)

        
        
    def process_twitch_command(self, message_content: str, user_name: str):
        command = message_content.split(" ")[0]
        args = message_content.split(" ")[1:]
        if command == "!clip":
            if self.last_clip_time + self.COMMAND_COOLDOWN > time.time():
                self.send_twitch_message(f"Sorry {user_name}, you can only clip once every {self.COMMAND_COOLDOWN} seconds.")
                return
            self.last_clip_time = time.time()
            self.generate_twitch_clip(user_name)
        if command == "!so" or command == "!shoutout":
            self.send_twitch_shoutout(args, user_name=None)
    
