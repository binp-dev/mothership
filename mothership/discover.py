from __future__ import annotations
from typing import Any, Sequence, List, Dict

from dataclasses import dataclass

import socket
import asyncio
from asyncio import DatagramProtocol, BaseTransport


@dataclass
class Info:
    addr: str
    uptime: float


async def discover() -> List[Info]:
    hosts: List[Info] = []

    class BeaconProtocol(DatagramProtocol):
        def connection_made(self, sock: BaseTransport) -> None:
            print(f"Connected: {sock}")

        def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
            print(f"Received: {data!r} from {addr}")
            if data.startswith(b"\xbc"):
                pass
            elif data.startswith(b"\xcb") and len(data) >= 5:
                if isinstance(addr[0], str):
                    uptime = int.from_bytes(data[1:], "big")
                    hosts.append(Info(addr[0], uptime))
                else:
                    print("Unsupported address")
            else:
                print("Unsupported message")

    loop = asyncio.get_running_loop()
    sock = (
        await loop.create_datagram_endpoint(
            BeaconProtocol,
            local_addr=("0.0.0.0", 9696),
            family=socket.AF_INET,
            reuse_port=True,
            allow_broadcast=True,
        )
    )[0]
    sock.sendto(b"\xbc", ("255.255.255.255", 9696))
    await asyncio.sleep(1.0)
    sock.close()

    return hosts


def get_macs(addrs: Sequence[str]) -> List[str | None]:
    addr_to_mac: Dict[str, str] = {}
    with open("/proc/net/arp", "r") as f:
        f.readline()
        for line in f.readlines():
            parts = line.split()
            assert parts[0] not in addr_to_mac
            addr_to_mac[parts[0]] = parts[3]
    return [addr_to_mac.get(a) for a in addrs]


async def find_devices() -> Dict[str, Info]:
    devices: Dict[str, Info] = {}
    discovered = await discover()
    macs = get_macs([i.addr for i in discovered])
    for mac, info in zip(macs, discovered):
        if mac is not None:
            assert mac not in devices
            devices[mac] = info
        else:
            print(f"Cannot find MAC for {info.addr}")
    return devices


if __name__ == "__main__":
    for mac, info in asyncio.run(find_devices()).items():
        print(f"MAC\tIP\tUptime")
        print(f"{mac}\t{info.addr}\t{info.uptime} sec")
