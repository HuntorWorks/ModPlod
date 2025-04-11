from core.utils import mp_print
import hashlib
from core.shared_managers import twitch_api_manager

class BarryAIEventHandler:
    def __init__(self, character):
        self.character = character
        
        mp_print.debug("initializing Barry Event Handler loaded {self.character}")

        self.last_follow_event = {}
        self.recent_follow_hashes = set()

        self.context_prompt = """
        You are present and active on BeerHuntor's twitch channel.
        Give a direct response to the following message without emojis or prefix/suffix as though you were having a conversation with the user.
        Include the user's name and what they have done (subscribed, followed, gifted, etc) in your response, with the particulars (tier, number of gifts, etc)
        """

    def on_twitch_follow_event(self, payload: dict):
        import json
        raw_event = json.dumps(payload, sort_keys=True).encode("utf-8")
        event_hash = hashlib.sha256(raw_event).hexdigest()

        if event_hash in self.recent_follow_hashes:
            mp_print.warning(f"Duplicate follow event ignored for {payload.get('user_name', 'unknown')}")
            return
        self.recent_follow_hashes.add(event_hash)


        prompt = f"{self.context_prompt}, Message: {payload.get('user') } has followed BeerHuntor's channel."
        response = self.character.get_gpt_string_response(msg_to_respond=prompt, chat_history=False)
        self.character.speak(response)

    def on_twitch_subscribe_event(self, payload: dict):
        if payload.get('subscription_tier') == "1000":
            tier = "Tier 1"
        elif payload.get('subscription_tier') == "2000":
            tier = "Tier 2"
        else:
            tier = "Tier 3"

        prompt = f"{self.context_prompt}, Message: {payload.get('user') } has subscribed to BeerHuntor's channel, at tier {tier}."
        response = self.character.get_gpt_string_response(msg_to_respond=prompt, chat_history=False)
        self.character.speak(response)

    def on_twitch_subscribe_gift_event(self, payload: dict):
        prompt = f"{self.context_prompt}, Message: {payload.get('user') } has gifted {payload.get('gift_count')} subscriptions to BeerHuntor's channel. They have gifted {payload.get('total_gifts_count')} subscriptions in total."
        response = self.character.get_gpt_string_response(msg_to_respond=prompt, chat_history=False)
        self.character.speak(response)

    def on_twitch_subscription_message_event(self, payload: dict):
        prompt = f"{self.context_prompt}, Message: {payload.get('user') } has sent a message when they subscribed to BeerHuntor's channel it said: {payload.get('message')}"
        response = self.character.get_gpt_string_response(msg_to_respond=prompt, chat_history=False)
        self.character.speak(response)

class BarryAIHandler:
    def __init__(self, character):
        self.character = character
        self.twitch_api_manager = twitch_api_manager
        self.recent_hashes = set()
        self.static_triggers = { 
            "follow me" : 
                {"action": "timeout", 
                "reason": "Self-promo", 
                "duration": 30
                },
            "here is my discord username" : 
                {"action": "timeout", 
                "reason": "Self-promo", 
                "duration": 30
                },
            "adding me on discord" : 
                {"action": "timeout", 
                "reason": "Self-promo", 
                "duration": 30
                },
            "request on discord" : 
                {"action": "timeout", 
                "reason": "Self-promo", 
                "duration": 30
                },
        }
        self.regex_triggers = {
            {"pattern": r"(https?:\/\/)?(www\.)?(discord\.gg|discord\.com\/invite)", "action": "timeout", "reason": "Discord link", "duration": 60},
            {"pattern": r"([a-zA-Z])\1{4,}", "action": "timeout", "reason": "Stop spamming", "duration": 20},
            {"pattern": r"(https?:\/\/|www\.)[^\s]+", "action": "timeout", "reason": "Posting links is not allowed", "duration": 30}
        }

    def on_message_received(self, payload: dict):
        try: 
            message_content = payload.get('message')
            user_name = payload.get('user_name')
            user_id = payload.get('user_id')
            
            if self.check_auto_mod(message_content, user_id):
                self.character.speak(f"Hey {user_name}, please don't post links or spam in chat. Thanks!")

        except ValueError:
            mp_print.error("Error processing message: {payload}")
            return
        
    def check_auto_mod(self, message_content: str, user_id: str) -> bool:
        import re
        message_lower = message_content.lower()

        #Check against static triggers
        for phrase, trigger in self.static_triggers.items():
            if phrase in message_lower:
                self.twitch_api_manager.send_twitch_timeout(user_id=user_id, duration=trigger["duration"], reason=trigger["reason"])
                return True

        #Check against regex triggers
        for trigger in self.regex_triggers:
            if re.search(trigger["pattern"], message_lower):
                self.twitch_api_manager.send_twitch_timeout(user_id=user_id, duration=trigger["duration"], reason=trigger["reason"])
                return True
        return False
