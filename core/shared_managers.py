from core.twitch_api_manager import TwitchAPIManager
from bots.chat_bot.twitch_chat_actions_manager import TwitchChatActionsManager
from core.obs_websocket_manager import OBSWebsocketManager
from core.openai_manager import OpenAIManager
from bots.gpt_character import Character
from bots.barry_ai.barry_event_handler import BarryAIEventHandler, BarryAIHandler
from core.utils import mp_print
from bots.barry_ai.barry_ai_state import BarryAIState
from bots.chat_bot.twitch_bot_state import TwitchBotState

import asyncio

twitch_api_manager = TwitchAPIManager()
twitch_ai_actions_manager = TwitchChatActionsManager()
obs_manager = OBSWebsocketManager()
openai_manager = OpenAIManager()

#CHARACTER
barry_ai = Character("Barry Braintree")
mp_print.debug(f"Barry AI loaded: {barry_ai}")
barry_ai_event_handler = BarryAIEventHandler(barry_ai)
barry_ai_handler = BarryAIHandler(barry_ai, twitch_api_manager) 

#STATES
barry_state = BarryAIState()
twitch_bot_state = TwitchBotState()

twitch_api_manager.set_actions_manager(twitch_ai_actions_manager)
twitch_ai_actions_manager.set_event_handler(barry_ai_handler)
