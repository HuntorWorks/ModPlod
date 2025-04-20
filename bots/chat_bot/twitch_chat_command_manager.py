from core.utils import get_str_from_args
import time

class TwitchChatCommandManager: 

    def __init__(self, actions_manager):
        self.actions_manager = actions_manager
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

    def process_twitch_command(self, message_content: str, user_name: str, user_id: str):
        command = message_content.split(" ")[0].lower()
        args = message_content.split(" ")[1:]
        if command == "!clip":
            if self.can_send_command("clip"):
                self.actions_manager.generate_twitch_clip(user_name)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only clip once every {self.command_cooldowns['clip']} seconds.")
        if command == "!so" or command == "!shoutout":
            if self.can_send_command("so"):
                self.actions_manager.send_twitch_shoutout(args, user_name=user_name)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only shoutout once every {self.command_cooldowns['so']} seconds.")
        if command == "!followage":
            if self.can_send_command("followage"):
                self.actions_manager.send_twitch_followage(user_name, user_id)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only get followage once every {self.command_cooldowns['followage']} seconds.")
        if command == "!title":
            title = get_str_from_args(args)
            if self.can_send_command("title"):
                self.actions_manager.set_twitch_channel_title(user_name, title=title)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only change the title once every {self.command_cooldowns['title']} seconds.")
        if command == "!game":
            game = get_str_from_args(args)
            if self.can_send_command("game"):
                self.actions_manager.set_twitch_channel_game(user_name, game=game)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only change the game once every {self.command_cooldowns['game']} seconds.")
        if command == "!ban":
            user_to_ban = args[0]
            reason = get_str_from_args(args[1:])
            if self.can_send_command("ban"):
                self.actions_manager.send_twitch_ban_user(user_name, user_to_ban, reason=reason)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only ban once every {self.command_cooldowns['ban']} seconds.")
        if command == "!timeout":
            user_to_timeout, reason, duration = self.parse_timeout_command(args)
            if self.can_send_command("timeout"):
                self.actions_manager.send_twitch_timeout_user(user_name=user_name, user_to_timeout=user_to_timeout, reason=reason, duration=duration)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only timeout once every {self.command_cooldowns['timeout']} seconds.")
        if command == "!unban":
            user_to_unban = args[0]
            if self.can_send_command("unban"):
                self.actions_manager.send_twitch_unban_user(user_name=user_name, user_to_unban=user_to_unban)
            else:
                self.actions_manager.send_twitch_message(f"Sorry {user_name}, you can only unban once every {self.command_cooldowns['unban']} seconds.")

        
    def parse_timeout_command(self, args: list):
        try:
            user = args[0] # user to timeout
            duration = int(args[-1])
        except ValueError:
            raise ValueError("Invalid command format. Must be !timeout <user> <reason> <duration>")
        reason = get_str_from_args(args[1:-1])

        return user, reason, duration
    
        #FUTURE: Add per user cooldowns if it is needed.
    def can_send_command(self, command: str) -> bool: 
        now = time.time()
        last_command_time = self.last_command_times.get(command, 0)
        cooldown = self.command_cooldowns.get(command, 0)

        if now - last_command_time >= cooldown:
            self.last_command_times[command] = now
            return True
        return False