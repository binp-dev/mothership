from __future__ import annotations
from typing import Tuple, List

from pathlib import Path
import json

import asyncio
from aiohttp import web

from mothership.hosts import Mac
from mothership.config import Config
from .daemon import Daemon


class App(web.Application):
    def __init__(self, config: Config) -> None:
        super().__init__()

        self.daemon = Daemon(config, self._daemon_updated)
        self.clients: List[web.WebSocketResponse] = []

        self.files_path = Path(__file__).parent.resolve() / "static"
        self.add_routes(
            [
                web.get("/websocket", self._websocket_handler),
                web.get("/hosts", self._hosts_handler),
                web.get("/", self._index_handler),
                web.static("/", self.files_path, append_version=True),
            ]
        )

    async def _index_handler(self, request: web.Request) -> web.FileResponse:
        return web.FileResponse(self.files_path / "index.html")

    async def _hosts_handler(self, request: web.Request) -> web.Response:
        return web.json_response(self.daemon.dump_hosts())

    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        print("Websocket connected")
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        print("Websocket upgraded")
        self.clients.append(ws)

        try:
            await ws.send_str(json.dumps(self.daemon.dump_hosts()))
            async for msg in ws:
                print(msg)
                if msg.type == web.WSMsgType.TEXT:
                    print(f"Websocket message: {msg.data}")
                    req = json.loads(msg.data)
                    if req["type"] == "reboot":
                        if req["target"] == "all":
                            self.daemon.reboot_all()
                        else:
                            self.daemon.reboot(Mac(req["target"]))
                    elif req["type"] == "update":
                        if req["target"] == "all":
                            self.daemon.update_all()
                        else:
                            self.daemon.update(Mac(req["target"]))
                    else:
                        print(f"Unknown request type")
                elif msg.type == web.WSMsgType.CLOSE:
                    break
        finally:
            self.clients.remove(ws)
            print("Websocket closed")
            await ws.close()

        return ws

    async def _daemon_updated(self) -> None:
        data = json.dumps(self.daemon.dump_hosts())
        count = 0
        for ws in self.clients:
            try:
                await ws.send_str(data)
                count += 1
            except RuntimeError as e:
                print(f"Error sending update to client: {e}")
        print(f"Update sent to {count} clients")

    async def run(self, addr: Tuple[str, int]) -> None:
        runner = web.AppRunner(self)
        await runner.setup()
        site = web.TCPSite(runner, addr[0], addr[1])
        await site.start()
        await self.daemon.run()
