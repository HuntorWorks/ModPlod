from core.twitch_api_manager import TwitchAPIManager
from core.twitch_ai_actions_manager import TwitchAIActionsManager
from core.obs_websocket_manager import OBSWebSocketManager
from core.openai_manager import OpenAIManager

twitch_api_manager = TwitchAPIManager()
twitch_actions_manager = TwitchAIActionsManager()
obs_manager = OBSWebSocketManager()
openai_manager = OpenAIManager()


