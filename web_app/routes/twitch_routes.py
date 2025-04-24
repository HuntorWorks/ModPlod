from flask import Blueprint, request, jsonify
from core.utils import run_async_tasks
from core.shared_managers import twitch_api_manager, barry_ai_event_handler
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
    mp_print.sys_message("Twitch follow EventSub fired!")
    data = request.get_json(force=True)
    print(data)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}

    if "event" in data:
        payload = {
            "user": data["event"].get("user_name", "unknown"),
            "user_id": data["event"].get("user_id", "unknown")
        }     
        barry_ai_event_handler.on_twitch_follow_event(payload)

    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscribe', methods=["POST"])
def twitch_eventsub_callback_subscribe():
    data = request.get_json(force=True)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        payload = {
            "user": data["event"].get("user_name", "unknown")   ,
            "subscription_tier": data["event"].get("tier", "unknown"),
            "is_gift_sub": data["event"].get("is_gift", "unknown")
        }
        barry_ai_event_handler.on_twitch_subscribe_event(payload)
        
        
    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscribe_gift', methods=["POST"])
def twitch_eventsub_callback_subscribe_gift():
    data = request.get_json(force=True)
    print(data)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        payload = {
            "user": data["event"].get("user_name", "unknown"),
            "tier": data["event"].get("tier", "unknown"),
            "gift_count": data["event"].get("total", 0),
            "total_gifts_count": data["event"].get("cumulative_total", 0)
        }

        barry_ai_event_handler.on_twitch_subscribe_gift_event(payload)

    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/subscription_msg', methods=["POST"])
def twitch_eventsub_callback_subscription_msg():
    data = request.get_json(force=True)
    print(data)

    if "challenge" in data:
        return data["challenge"], 200, {'Content-Type': 'text/plain'}
    
    if "event" in data:
        payload = {
            "user": data["event"].get("user_name", "unknown"),
            "message": data["event"].get("message", "unknown")
        }
        barry_ai_event_handler.on_twitch_subscription_message_event(payload)


    return jsonify({"status": "ok"}), 200

@twitch_routes.route('/twitch/eventsub/callback/incoming_raid', methods=["POST"])
def twitch_eventsub_callback_incoming_raid(): 
    data = request.get_json(force=True)
    print(data)

    if "event" in data: 
        payload = { 
            "raiding_user": data["event"].get("from_broadcaster_user_name", "unknown"),
            "raiding_viewers": data["event"].get("viewers", "unknown") 
        }
        barry_ai_event_handler.on_twitch_raid_event(payload)
    else : 
        return jsonify ({"status": "failed no event found"})
    return jsonify({"status": "ok"}), 200

#region ADMIN ROUTES
@twitch_routes.route('/twitch/admin/subscribe_to_eventsub_follow', methods=["POST"])
def twitch_admin_subscribe_to_eventsub_follow():
    result = run_async_tasks(twitch_api_manager.subscribe_to_eventsub_follow())

    if result is False:
        return jsonify({"status": "error", "message": "Failed to subscribe to eventsub follow"}), 500   
    return jsonify({"status": "success", "message": "Event subscribed"})

@twitch_routes.route('/twitch/admin/unsubscribe_to_all_eventsub', methods=["POST"])
def unsubscribe_all_eventsubs():
    import requests
    from core.utils import run_async_tasks
    from flask import jsonify

    access_token = run_async_tasks(twitch_api_manager.get_app_access_token())

    headers = {
        "Client-ID": twitch_api_manager.bot_client_id,
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers)
    subs = response.json().get("data", [])

    print(f"[ModPlod-INFO]: Found {len(subs)} subscriptions to remove...")

    for sub in subs:
        print(f"→ Removing: {sub['type']} | ID: {sub['id']}")
        del_resp = requests.delete(f"https://api.twitch.tv/helix/eventsub/subscriptions?id={sub['id']}", headers=headers)
        if del_resp.status_code == 204:
            print(f"✅ Deleted {sub['id']}")
        else:
            print(f"❌ Failed to delete {sub['id']}: {del_resp.status_code} - {del_resp.text}")

    return jsonify({"status": "success", "message": f"Attempted to delete {len(subs)} EventSubs."})
#endregion
