from enum import Enum
import os 
from dotenv import load_dotenv

load_dotenv()

class Mode(Enum): 
    DEV = "dev"
    LIVE = "live"

class Priority(Enum): 
    HIGH = "high_priority"
    MEDIUM = "medium_priority"
    LOW = "low_priority"

class Mood(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANNOYED = "annoyed"
    GRUMPY = "grumpy"

APP_MODE = Mode(os.getenv("MODPLOD_ENV", "dev").lower())

NGROK_DEV_TUNNEL_URL = "https://0f37-86-24-211-32.ngrok-free.app" #port 5001 ->  http://localhost:5001
NGROK_LIVE_TUNNEL_URL = "https://a76b-86-24-211-32.ngrok-free.app" # -> http://localhost:5000

