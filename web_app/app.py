from quart import Quart
from web_app.routes.voice_routes import voice_routes
from web_app.routes.twitch_routes import twitch_routes
from web_app.routes.core_routes import core_routes
from core.utils import mp_print

app = Quart(__name__)
app.register_blueprint(voice_routes, url_prefix='/')
app.register_blueprint(twitch_routes, url_prefix='/')
app.register_blueprint(core_routes, url_prefix='/')

