from __future__ import annotations

import asyncio

from uvicorn import Config, Server
from asgiref.wsgi import WsgiToAsgi

from . import app, start

asgi_app = WsgiToAsgi(app)  # type: ignore

config = Config(f"{__name__}:asgi_app", host="0.0.0.0", port=5000, log_level="debug")
server = Server(config)

asyncio.run(start(server.serve()))
