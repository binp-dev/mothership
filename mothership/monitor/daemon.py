from __future__ import annotations
from typing import Sequence

from dataclasses import dataclass

import socket
import asyncio

from mothership.tree import Device


@dataclass
class Beacon:
    expires: int
    period: int

    def pack(self) -> bytes:
        return b"\xbc" + self.expires.to_bytes(2) + self.period.to_bytes(2)


@dataclass
class Daemon:
    devices: Sequence[Device]

    async def run(self) -> None:
        asyncio.create_task(self._beacon_loop())
        print(f"Daemon started")

    async def _beacon_loop(self) -> None:
        loop = asyncio.get_running_loop()

        period = 30
        msg = Beacon(2 * period, 4)
        sock = (
            await loop.create_datagram_endpoint(
                asyncio.DatagramProtocol,
                local_addr=("0.0.0.0", 9696),
                family=socket.AF_INET,
                reuse_port=True,
                allow_broadcast=True,
            )
        )[0]
        while True:
            print(f"Beacon")
            sock.sendto(msg.pack(), ("255.255.255.255", 9696))
            await asyncio.sleep(period)
