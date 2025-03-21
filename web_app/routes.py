import os
import sys
from flask import request
from dotenv import load_dotenv

from core.twitch_api_manager import TwitchAPIManager

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "bots"))

from bots.gpt_character import Character
from flask import jsonify, Blueprint

api_blueprint = Blueprint("api", __name__)
load_dotenv()

barry_ai = Character(character_name="Barry Braintree")

twitch_api_manager = TwitchAPIManager()

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
    
@api_blueprint.route('/twitch/login', methods=["GET"])
def twitch_login():
    return jsonify({"auth_url": twitch_api_manager.get_auth_url()})
    
@api_blueprint.route('/twitch/auth', methods=["GET"])
def twitch_auth():
    auth_code = request.args.get('code')

    if not auth_code:
        return jsonify({"status": "error", "message": "No authorization code found"}), 400
    
    token_response = twitch_api_manager.exchange_code_for_token(auth_code)

    if "access_token" not in token_response: 
        return jsonify({
            "status": "error", 
            "message": "Failed to get access token", 
            "response": token_response
        }), 400
    
    return jsonify({"status": "success", "message": "Authentication successful", "access_token": token_response["access_token"]})
    
@api_blueprint.route('/twitch/chat', methods=["POST"])
def process_twitch_chat():
    pass

@api_blueprint.route('/twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass

@api_blueprint.route('/settings/update', methods=["POST"])
def update_character_settings():
    pass