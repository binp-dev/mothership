from __future__ import annotations

from pathlib import Path
import json

import asyncio
from flask import Flask, Response, send_from_directory

from mothership.config import Config
from .daemon import Daemon


DAEMON: Daemon


async def init(config: Config) -> None:
    global DAEMON
    DAEMON = Daemon(config)
    asyncio.create_task(DAEMON.run())


app = Flask(__name__)


@app.route("/")
def root() -> Response:
    return static_(Path("index.html"))


@app.route("/<path:path>")
def static_(path: Path) -> Response:
    return send_from_directory(Path(__file__).parent.resolve() / "static", path)


@app.route("/hosts")
def hosts() -> str:
    global DAEMON
    return json.dumps(DAEMON.flat_hosts())
