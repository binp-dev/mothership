from __future__ import annotations
from typing import Any, Awaitable

from pathlib import Path
import json
import toml

import asyncio
from flask import Flask, Response, send_from_directory

from mothership.config import Config
from mothership.tree import build_tree
from .daemon import Daemon


DAEMON: Daemon


app = Flask(__name__)


async def start(serve: Awaitable[None]) -> None:
    with open(Path("config.toml"), "r") as f:
        devices = build_tree(Config(**toml.load(f)))
    print(devices)

    global DAEMON
    DAEMON = Daemon(devices)
    asyncio.create_task(DAEMON.run())

    await serve


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
