import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "bots"))
#TODO: bots dir not recognised. Test API endpoints using postman
from bots.gpt_character import Character
from flask import Flask, request, jsonify, Blueprint

app = Flask(__name__)
api_blueprint = Blueprint("api", __name__)

barry_ai = Character(character_name="Barry Braintree")

@app.route('/voice/start/', methods=["POST"])
def start_voice_rec():
    try:
        stop_rec_key = 'p'
        user_input = barry_ai.handle_mic_input(stop_rec_key)
        return jsonify({"status": "success", "message": user_input})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/voice/stop/', methods=["POST"])
def stop_voice_rec():
    try:
        barry_ai.speech_to_text.stop_recording_mic()
        return jsonify({"status": "success", "message": "Recording Stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/twitch/chat', methods=["POST"])
def process_twitch_chat():
    pass

@app.route('twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass

@app.route('settings/update', methods=["POST"])
def update_character_settings():
    pass