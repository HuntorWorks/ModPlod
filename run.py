import sys
import os
import asyncio
from core.utils import mp_print
from enum import Enum


from core.constants import APP_MODE, Mode
PORT = 5001 if APP_MODE == Mode.DEV else 5000
mp_print.info(f"[BOOT] Modplod Lauched in {APP_MODE.value.upper()} mode")

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.shared_managers import twitch_api_manager, barry_ai
from web_app.app import app
from web_app.obs_window import start_obs_audio_window
import threading

def start_audio_window():
    thread=threading.Thread(target=start_obs_audio_window, daemon=True, name="OBS Audio Window")
    thread.start()

async def start_barry() : 
    await barry_ai.start()

async def main(port=5000) : 
    mp_print.info(f"[Main] Starting up..")
    
    start_audio_window()
    mp_print.info(f"[Main] Audio window Started")

    twitch_api_manager.start_twitch_api_manager()
    await barry_ai.start()
    mp_print.info(f"[Main] Barry started")

    await app.run_task(
          host="0.0.0.0", 
          port=port, 
          certfile="cert.pem",
          keyfile="key.pem",
    )
    mp_print.info(f"[Main] Quart app started")

if __name__ == "__main__":
    asyncio.run(main())
