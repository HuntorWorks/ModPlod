from flask import Flask, request
from web_app.routes.voice_routes import voice_routes
from web_app.routes.twitch_routes import twitch_routes
from web_app.routes.core_routes import core_routes
import asyncio
from core.utils import mp_print


app = Flask(__name__)
app.register_blueprint(voice_routes, url_prefix='/')
app.register_blueprint(twitch_routes, url_prefix='/')
app.register_blueprint(core_routes, url_prefix='/')

# import sys
# import traceback
# import threading
# mp_print.info(f"=== ACTIVE THREADS ===")
# for thread in threading.enumerate():
#     mp_print.info(f"-{thread.name} (Deamon: {thread.daemon})")
#     stack = sys._current_frames()[thread.ident]
#     if stack: 
#         traceback.print_stack(stack)
# mp_print.info(f"=== END ACTIVE THREADS ===")
