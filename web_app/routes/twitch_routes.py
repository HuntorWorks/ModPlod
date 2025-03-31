from flask import Blueprint, request, jsonify
from core.utils import run_async_tasks
from core.shared_managers import twitch_api_manager
from core.utils import mp_print
import json

twitch_routes = Blueprint("twitch_routes", __name__)


@twitch_routes.route('/twitch/chat', methods=["POST"])
def process_twitch_chat():
    pass

@twitch_routes.route('/twitch/send_message', methods=["POST"])
def send_twitch_message():
    try:
        message = "Test Send Message"
        run_async_tasks(twitch_api_manager.send_message(message))
        
        return jsonify({"status": "success", "message": "Message sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@twitch_routes.route('/twitch/send_whisper', methods=["POST"])
def send_twitch_whisper():
    pass

@twitch_routes.route('/twitch/send_whisper_to_all', methods=["POST"])
def send_twitch_whisper_to_all():
    pass

@twitch_routes.route('/twitch/ban_user', methods=["POST"])
def send_twitch_ban_user():
    pass

@twitch_routes.route('/twitch/unban_user', methods=["POST"])
def send_twitch_unban_user():
    pass

@twitch_routes.route('/twitch/timeout_user', methods=["POST"])
def send_twitch_timeout_user():
    pass

@twitch_routes.route('/twitch/untimeout_user', methods=["POST"])
def send_twitch_untimeout_user():
    pass

@twitch_routes.route('/twitch/add_blocked_term', methods=["POST"])
def send_twitch_add_blocked_term():
    pass    

@twitch_routes.route('/twitch/remove_blocked_term', methods=["POST"])
def send_twitch_remove_blocked_term():
    pass

@twitch_routes.route('/twitch/create_clip', methods=["POST"])
def send_twitch_create_clip():
    try:
        broadcast_id = run_async_tasks(twitch_api_manager.get_broadcast_id_from_name())
        mp_print.debug(f"Final broadcast_id in route: : {repr(broadcast_id)}")

        if not broadcast_id:
            return jsonify({"status": "error", "message": "No broadcast ID found"})
        
        clip_result = run_async_tasks(twitch_api_manager.create_clip(broadcast_id))#

        return jsonify({
            "status": "success", 
            "message": "Clip created", 
            "broadcast_id": broadcast_id, 
            "clip_result": clip_result
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
    
@twitch_routes.route('/settings/update', methods=["POST"])
def update_character_settings():
    pass

@twitch_routes.route('/twitch/moderation', methods=["POST"])
def twitch_moderation():
    pass