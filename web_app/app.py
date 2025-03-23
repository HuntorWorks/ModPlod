from flask import Flask
from web_app.obs_window import start_obs_audio_window
from web_app.routes import api_blueprint
from core.twitch_api_manager import TwitchAPIManager
import threading

print("App started")


app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/')

def start_audio_window():
    thread=threading.Thread(target=start_obs_audio_window, daemon=True)
    thread.start()
    
if __name__ != "__main__":
    start_audio_window()
    print(app.url_map)
    app.run(host="0.0.0.0", port=5000, use_reloader=False)
else: 
    pass

