import requests
import os
print(f"Twitch Client Secret: {os.getenv('TWITCH_CLIENT_SECRET')}")
import urllib.parse
from dotenv import load_dotenv


class TwitchAPIManager:
    CLIENT_ID = None
    CLIENT_SECRET = None
    BOT_ID = None
    OWNER_ID = None
    def __init__(self):
        load_dotenv()

    def get_auth_url(self):
        scopes = [
            "moderator:manage:banned_users",
            "chat:read",
            "chat:edit"
        ]

        scope_param = urllib.parse.quote_plus(" ".join(scopes))

        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize?"
            f"client_id={os.getenv('TWITCH_CLIENT_ID')}"
            f"&redirect_uri={os.getenv('TWITCH_REDIRECT_URI')}"
            f"&response_type=code"
            f"&scope={scope_param}"
        )

        return auth_url
    
    def exchange_code_for_token(self, code):
        token_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": os.getenv("TWITCH_CLIENT_ID"),
            "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("TWITCH_REDIRECT_URI")
        }

        print(f"Sending Token Request: {params}")

        response = requests.post(token_url, data=params)

        print(f"Received Token Response: {response.json()}")
        return response.json()