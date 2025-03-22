import requests
import os
import time
import json
import urllib.parse
from dotenv import load_dotenv


class TwitchAPIManager:
    def __init__(self):
        load_dotenv()  # ✅ Load environment variables
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.redirect_uri = os.getenv("TWITCH_AUTH_REDIRECT_URI")
        self.token_data = self.load_token()  # ✅ Load existing token

    def load_token(self):
        """Load the saved token from a file if valid."""
        try:
            with open("token.json", "r") as file:
                token_data = json.load(file)
                if token_data.get("expires_at", 0) > time.time():
                    print("✅ Loaded valid token.")
                    return token_data
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None  # No valid token found

    def save_token(self, token_data):
        """Save the token for future use."""
        token_data["expires_at"] = time.time() + token_data["expires_in"]
        with open("token.json", "w") as file:
            json.dump(token_data, file)
        print("💾 Token saved to token.json")

    def get_token(self):
        """Retrieve a valid token (refresh if expired)."""
        if self.token_data and self.token_data["expires_at"] > time.time():
            return self.token_data["access_token"]

        print("🔄 Getting a new token...")
        new_token = self.get_app_access_token()
        if new_token:
            self.token_data = new_token
            self.save_token(new_token)
            return new_token["access_token"]
        return None

    def get_app_access_token(self):
        """Automatically get an OAuth token without manual login."""
        token_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        response = requests.post(token_url, data=params)
        token_data = response.json()

        if "access_token" not in token_data:
            print(f"⚠ ERROR: Failed to get access token: {token_data}")
            return None
        
        print(f"✅ Got App Access Token: {token_data['access_token']}")
        return token_data

    def get_auth_url(self):
        """Generate Twitch OAuth URL."""
        scopes = [
            "moderator:manage:banned_users",
            "chat:read",
            "chat:edit"
        ]

        scope_param = urllib.parse.quote_plus(" ".join(scopes))

        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize?"
            f"client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={scope_param}"
        )

        return auth_url

    def exchange_code_for_token(self, code):
        """Exchange the Twitch auth code for an access token (User OAuth)."""
        token_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        print(f"📡 Sending Token Request: {params}")
        response = requests.post(token_url, data=params)
        token_data = response.json()

        if "access_token" not in token_data:
            print(f"⚠ ERROR: Failed to exchange code for token: {token_data}")
            return None

        print(f"✅ Got User OAuth Access Token: {token_data['access_token']}")
        self.save_token(token_data)  # Save user token
        return token_data
