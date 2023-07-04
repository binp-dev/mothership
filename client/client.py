from __future__ import annotations
from typing import Any

import socket
import asyncio


class BeaconProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        print(f"Connection made: {transport}")

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        print(f"Datagram received: {data!r} from {addr}")


async def main() -> None:
    loop = asyncio.get_running_loop()
    sock = (
        await loop.create_datagram_endpoint(
            BeaconProtocol,
            local_addr=("0.0.0.0", 9696),
            family=socket.AF_INET,
            allow_broadcast=True,
            reuse_port=True,
        )
    )[0]
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
