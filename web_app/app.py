from flask import Flask
from obs_window import start_obs_audio_window
from routes import api_blueprint
import sys
import threading

app = Flask(__name__)
app.register_blueprint(api_blueprint)

def start_audio_window():
    threading.Thread(target=start_obs_audio_window, daemon=True).start()

if __name__ == "__main__":
    start_audio_window()
    app.run(host="0.0.0.0", port=5000)



