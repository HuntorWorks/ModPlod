from flask import Blueprint, request, jsonify
from core.utils import mp_print
from core.shared_managers import barry_ai

voice_routes = Blueprint("voice_routes", __name__)

@voice_routes.route('/voice/start', methods=["POST"])
def start_voice_rec():
    try:
        stop_rec_key = 'p'
        user_input = barry_ai.handle_mic_input(stop_rec_key)
        return jsonify({"status": "success", "message": user_input})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@voice_routes.route('/voice/stop', methods=["POST"])
def stop_voice_rec():
    try:
        barry_ai.speech_to_text.stop_recording_mic()
        return jsonify({"status": "success", "message": "Recording Stopped"})
    except Exception as e:
        return jsonify({"status": "error", "Could not stop recording": str(e)}), 500
