from uvicorn import Server, Config as ServerConfig
from asgiref.wsgi import WsgiToAsgi

from mothership.config import Config as AppConfig
from .app import app, init

async_app = WsgiToAsgi(app)  # type: ignore

config = ServerConfig(
    f"{__name__}:async_app",
    host="0.0.0.0",
    port=5000,
    log_level="debug",
)
server = Server(config)


async def run(config: AppConfig) -> None:
    await init(config)
    await server.serve()
