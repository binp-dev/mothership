from __future__ import annotations
from typing import Tuple

from pathlib import Path
import json

import asyncio
from aiohttp import web

from mothership.config import Config
from .daemon import Daemon


class App(web.Application):
    def __init__(self, config: Config) -> None:
        super().__init__()

        self.daemon = Daemon(config)

        self.files_path = Path(__file__).parent.resolve() / "static"
        self.add_routes(
            [
                web.get("/hosts", self.hosts),
                web.get("/", self.index),
                web.static("/", self.files_path, append_version=True),
            ]
        )

    async def index(self, request: web.Request) -> web.FileResponse:
        return web.FileResponse(self.files_path / "index.html")

    async def hosts(self, request: web.Request) -> web.Response:
        return web.Response(text=json.dumps(self.daemon.flat_hosts()))

    async def run(self, addr: Tuple[str, int]) -> None:
        runner = web.AppRunner(self)
        await runner.setup()
        site = web.TCPSite(runner, addr[0], addr[1])
        await site.start()
        await self.daemon.run()
