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
    """Return the Twitch OAuth login URL for manual authentication."""
    return jsonify({"auth_url": twitch_api_manager.get_auth_url()})

@api_blueprint.route('/twitch/auth', methods=["GET"])
def twitch_auth():
    """Handle Twitch authentication callback and exchange the auth code."""
    auth_code = request.args.get('code')

    if not auth_code:
        return jsonify({"status": "error", "message": "No authorization code found"}), 400

    token_response = twitch_api_manager.exchange_code_for_token(auth_code)

    if not token_response or "access_token" not in token_response:
        return jsonify({
            "status": "error",
            "message": "Failed to get access token",
            "response": token_response
        }), 400

    return jsonify({"status": "success", "message": "Authentication successful", "access_token": token_response["access_token"]})

@api_blueprint.route('/twitch/token', methods=["GET"])
def get_access_token():
    """Return the currently saved or refreshed Twitch access token."""
    access_token = twitch_api_manager.get_token()
    if not access_token:
        return jsonify({"status": "error", "message": "Failed to get valid token"}), 400
    return jsonify({"status": "success", "access_token": access_token})
    
@api_blueprint.route('/twitch/chat', methods=["POST"])
def process_twitch_chat():
    pass

@api_blueprint.route('/twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass

@api_blueprint.route('/settings/update', methods=["POST"])
def update_character_settings():
    pass