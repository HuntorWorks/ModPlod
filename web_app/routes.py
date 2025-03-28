from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
from bots.gpt_character import Character
import asyncio

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

@api_blueprint.route('/twitch/send_message', methods=["POST"])
def send_twitch_message():
    try:
        message = "Test Send Message"
        
        asyncio.run(twitch_api_manager.send_message(message))
        
        return jsonify({"status": "success", "message": "Message sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_blueprint.route('/twitch/send_whisper', methods=["POST"])
def send_twitch_whisper():
    pass

@api_blueprint.route('/twitch/send_whisper_to_all', methods=["POST"])
def send_twitch_whisper_to_all():
    pass

@api_blueprint.route('/twitch/ban_user', methods=["POST"])
def send_twitch_ban_user():
    pass

@api_blueprint.route('/twitch/unban_user', methods=["POST"])
def send_twitch_unban_user():
    pass

@api_blueprint.route('/twitch/timeout_user', methods=["POST"])
def send_twitch_timeout_user():
    pass

@api_blueprint.route('/twitch/untimeout_user', methods=["POST"])
def send_twitch_untimeout_user():
    pass

@api_blueprint.route('/twitch/add_blocked_term', methods=["POST"])
def send_twitch_add_blocked_term():
    pass    


@api_blueprint.route('/twitch/remove_blocked_term', methods=["POST"])
def send_twitch_remove_blocked_term():
    pass

@api_blueprint.route('/twitch/create_clip', methods=["POST"])
def send_twitch_create_clip():
    pass


@api_blueprint.route('/settings/update', methods=["POST"])
def update_character_settings():
    pass

@api_blueprint.route('/twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass