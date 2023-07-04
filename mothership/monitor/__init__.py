from __future__ import annotations
from typing import Any, Awaitable

import asyncio
from pathlib import Path
from dataclasses import dataclass

import toml
from flask import Flask

from mothership.config import Config


@dataclass
class Context:
    config: Config


CONTEXT: Context


def ctx() -> Context:
    global CONTEXT
    return CONTEXT


app = Flask(__name__)


async def start(serve: Awaitable[None]) -> None:
    with open(Path("config.toml"), "r") as f:
        config = Config(**toml.load(f))
    print(config)

    global CONTEXT
    CONTEXT = Context(config)

    await serve


@app.route("/")
async def root() -> str:
    return str(ctx().config)
