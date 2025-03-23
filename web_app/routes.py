import os
import sys
from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
from bots.gpt_character import Character

from core.twitch_api_manager import TwitchAPIManager

api_blueprint = Blueprint("api", __name__)
load_dotenv()

barry_ai = Character(character_name="Barry Braintree")

twitch_api_manager = TwitchAPIManager()

@api_blueprint.route("/")
def home_page(): 
    return jsonify({"message": "Hello World"})

@api_blueprint.route('/voice/start', methods=["POST"])
def start_voice_rec():
    try:
        stop_rec_key = 'p'
        user_input = barry_ai.handle_mic_input(stop_rec_key)
        return jsonify({"status": "success", "message": user_input})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@api_blueprint.route('/voice/stop', methods=["POST"])
def stop_voice_rec():
    try:
        barry_ai.speech_to_text.stop_recording_mic()
        return jsonify({"status": "success", "message": "Recording Stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@api_blueprint.route('/twitch/chat', methods=["POST"])
def process_twitch_chat():
    pass


@api_blueprint.route('/twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass


@api_blueprint.route('/settings/update', methods=["POST"])
def update_character_settings():
    pass
