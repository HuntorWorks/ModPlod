from quart import jsonify, Blueprint

core_routes = Blueprint("api", __name__)

@core_routes.route('/', methods=["GET"])
async def home_page():
    return jsonify({"message": "Hello World"})

@core_routes.route('/shutdown', methods=["POST"])
async def exit_app():
    app.shutdown_app()
    return jsonify({"status": "success", "message": "App shutting down"})
