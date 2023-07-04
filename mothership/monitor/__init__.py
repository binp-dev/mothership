from __future__ import annotations
from typing import Any, Awaitable

import asyncio
from pathlib import Path
from dataclasses import dataclass

import toml
from flask import Flask

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
async def root() -> str:
    global DAEMON
    return str(DAEMON.servants)
