from flask import Flask
from web_app.obs_window import start_obs_audio_window
from web_app.routes import api_blueprint
from core.twitch_api_manager import TwitchAPIManager
import threading

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/')
twitch_api_manager = TwitchAPIManager()


def start_audio_window():
    thread=threading.Thread(target=start_obs_audio_window, daemon=True)
    thread.start()

if __name__ != "__main__":
    start_audio_window()
    twitch_api_manager.start_twitch_api_manager()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
else: 
    pass

