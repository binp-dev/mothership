from __future__ import annotations
from typing import Any

import socket
import asyncio
from asyncio import DatagramProtocol, BaseTransport, DatagramTransport


def uptime() -> float:
    with open("/proc/uptime", "r") as f:
        return float(f.readline().split()[0])


class BeaconProtocol(DatagramProtocol):
    def connection_made(self, sock: BaseTransport) -> None:
        print(f"Connected: {sock}")
        self.sock: DatagramTransport = sock  # type: ignore

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        print(f"Received: {data!r} from {addr}")
        if data.startswith(b"\xbc"):
            self.sock.sendto(b"\xcb" + int(uptime()).to_bytes(4, "big"), addr)
        else:
            print("Unsupported")


loop = asyncio.new_event_loop()
loop.create_task(
    loop.create_datagram_endpoint(
        BeaconProtocol,
        local_addr=("0.0.0.0", 9696),
        family=socket.AF_INET,
        allow_broadcast=True,
        reuse_port=True,
    )
)
loop.run_forever()
