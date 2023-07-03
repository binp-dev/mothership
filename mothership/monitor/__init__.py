from __future__ import annotations

import asyncio
from pathlib import Path

import toml
from flask import Flask

from mothership.config import Config


_CONFIG: Config | None = None


def config() -> Config:
    global _CONFIG
    if _CONFIG is None:
        with open(Path("config.toml"), "r") as f:
            config = Config(**toml.load(f))
        print(config)
        _CONFIG = config
    return _CONFIG


app = Flask(__name__)


@app.route("/")
def root() -> str:
    return str(config())
