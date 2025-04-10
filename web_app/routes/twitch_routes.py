from flask import Blueprint, request, jsonify
from core.utils import run_async_tasks
from core.shared_managers import twitch_api_manager
from core.utils import mp_print
import json

twitch_routes = Blueprint("twitch_routes", __name__)

@twitch_routes.route('/twitch/send_message', methods=["POST"])
def send_twitch_message():
    try:
        message = "Test Send Message"
        run_async_tasks(twitch_api_manager.send_message(message))
        
        return jsonify({"status": "success", "message": "Message sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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

@twitch_routes.route('/twitch/eventsub/callback', methods=["POST"])
def twitch_eventsub_callback():
    data = request.json
    return jsonify({"status": "success", "message": "Event received"})

@twitch_routes.route('/twitch/eventsub/callback/follow', methods=["POST"])
def twitch_eventsub_callback_follow():
    data = request.get_json(force=True)
    print(data)

    # 🔒 Respond to Twitch verification
    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}

    # ✅ Real follow event payload
    if "event" in data:
        user = data["event"].get("user_name", "unknown")
        mp_print.info(f"🎉 New follower: {user}")

    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscribe', methods=["POST"])
def twitch_eventsub_callback_subscribe():
    data = request.get_json(force=True)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        user = data["event"].get("user_name", "unknown")
        mp_print.info(f"🎉 New subscriber: {user}")
        subscription_tier = data["event"].get("tier", "unknown")
        mp_print.info(f"🎉 New subscription tier: {subscription_tier}")
        is_gift_sub = data["event"].get("is_gift", "unknown")
        mp_print.info(f"🎉 Gifted: {is_gift_sub}") 
        
    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscribe_gift', methods=["POST"])
def twitch_eventsub_callback_subscribe_gift():
    data = request.get_json(force=True)
    print(data)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        user = data["event"].get("user_name", "unknown")
        mp_print.info(f"🎉 New subscriber: {user}")
        tier = data["event"].get("tier", "unknown")
        mp_print.info(f"🎉 New subscription tier: {tier}")
        gift_count = data["event"].get("total", 0)
        total_gifts_count = data["event"].get("cumulative_total", 0)
        mp_print.info(f"🎉 Has gifted {gift_count} subscriptions, and has gifted {total_gifts_count} subscriptions in total")


    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscription_msg', methods=["POST"])
def twitch_eventsub_callback_subscription_msg():
    data = request.get_json(force=True)
    print(data)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        user = data["event"].get("user_name", "unknown")
        mp_print.info(f"🎉 New subscription message: {user}")
        message = data["event"].get("message", "unknown")
        message_text = message["text"]
        mp_print.info(f"🎉 New subscription message: {message_text}")

    return jsonify({"status": "ok"}), 200


#ADMIN ROUTES

@twitch_routes.route('/twitch/admin/subscribe_to_eventsub_follow', methods=["POST"])
def twitch_admin_subscribe_to_eventsub_follow():
    result = run_async_tasks(twitch_api_manager.subscribe_to_eventsub_follow())

    if result is False:
        return jsonify({"status": "error", "message": "Failed to subscribe to eventsub follow"}), 500   
    return jsonify({"status": "success", "message": "Event subscribed"})

