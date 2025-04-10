from core.twitch_api_manager import TwitchAPIManager
from core.twitch_ai_actions_manager import TwitchAIActionsManager
from core.obs_websocket_manager import OBSWebsocketManager
from core.openai_manager import OpenAIManager
from bots.gpt_character import Character
from bots.barry_ai.barry_event_handler import BarryAIEventHandler
from core.utils import mp_print

twitch_api_manager = TwitchAPIManager()
twitch_ai_actions_manager = TwitchAIActionsManager()
obs_manager = OBSWebsocketManager()
openai_manager = OpenAIManager()

#CHARACTER
barry_ai = Character("Barry Braintree")
mp_print.debug(f"Barry AI loaded: {barry_ai}")
barry_ai_event_handler = BarryAIEventHandler(barry_ai)


twitch_api_manager.set_actions_manager(twitch_ai_actions_manager)

