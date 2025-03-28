from flask import request, jsonify, Blueprint

core_routes = Blueprint("api", __name__)

@core_routes.route('/', methods=["GET"])
def home_page():
    return jsonify({"message": "Hello World"})

@core_routes.route('/shutdown', methods=["POST"])
def exit_app():
    app.shutdown_app()
    return jsonify({"status": "success", "message": "App shutting down"})
