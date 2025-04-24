from enum import Enum
import os 
from dotenv import load_dotenv

load_dotenv()

class Mode(Enum): 
    DEV = "dev"
    LIVE = "live"

APP_MODE = Mode(os.getenv("MODPLOD_ENV", "dev").lower())

NGROK_DEV_TUNNEL_URL = "https://3519-86-24-211-32.ngrok-free.app" #port 5001 ->  http://localhost:5001
NGROK_LIVE_TUNNEL_URL = "https://f33a-86-24-211-32.ngrok-free.app" # -> http://localhost:5000