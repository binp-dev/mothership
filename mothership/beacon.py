from __future__ import annotations
from typing import Any, List, Dict

from dataclasses import dataclass

import socket
import asyncio
from asyncio import DatagramProtocol, BaseTransport


def get_macs(addrs: List[str]) -> List[str | None]:
    addr_to_mac: Dict[str, str] = {}
    with open("/proc/net/arp", "r") as f:
        f.readline()
        for line in f.readlines():
            parts = line.split()
            assert parts[0] not in addr_to_mac
            addr_to_mac[parts[0]] = parts[3]
    return [addr_to_mac.get(a) for a in addrs]


@dataclass
class Reflex:
    mac: str
    addr: str
    info: Info


@dataclass
class Info:
    uptime: int


@dataclass
class Beacon:
    sock: asyncio.DatagramTransport
    proto: BeaconProtocol
    remote_port: int = 9696

    class BeaconProtocol(DatagramProtocol):
        def __init__(self) -> None:
            self.hosts: Dict[str, Info] = {}

        def connection_made(self, sock: BaseTransport) -> None:
            print(f"Connected: {sock}")

        def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
            print(f"Received: {data!r} from {addr}")
            if data[0] == 0x96 and len(data) >= 2:
                if data[1] == 0xEC or data[1] == 0xB0:
                    pass
                elif data[1] == 0xCE and len(data) >= 6:
                    if isinstance(addr[0], str):
                        uptime = int.from_bytes(data[2:6], "big")
                        self.hosts[addr[0]] = Info(uptime)
                    else:
                        print("Unsupported address")
                else:
                    print("Unsupported code")
            else:
                print("Bad format")

    @staticmethod
    async def connect(local_port: int = 9696) -> Beacon:
        loop = asyncio.get_running_loop()
        sock, proto = await loop.create_datagram_endpoint(
            Beacon.BeaconProtocol,
            local_addr=("0.0.0.0", local_port),
            family=socket.AF_INET,
            reuse_port=True,
            allow_broadcast=True,
        )
        return Beacon(sock, proto)

    def close(self) -> None:
        self.sock.close()

    async def discover(self) -> Dict[str, Info]:
        self.proto.hosts = {}
        self.sock.sendto(b"\x96\xEC", ("255.255.255.255", self.remote_port))
        await asyncio.sleep(1.0)
        hosts = self.proto.hosts
        self.proto.hosts = {}
        return hosts

    def reboot(self, addr: str) -> None:
        print(f"Sending reboot request to {addr}:{self.remote_port}")
        self.sock.sendto(b"\x96\xB0", (addr, self.remote_port))

    async def find_hosts(self) -> List[Reflex]:
        hosts: Dict[str, Reflex] = {}
        discovered = await self.discover()
        macs = get_macs([k for k in discovered.keys()])
        for mac, (addr, status) in zip(macs, discovered.items()):
            if mac is not None:
                assert mac not in hosts
                hosts[mac] = Reflex(mac, addr, status)
            else:
                print(f"Cannot find MAC for {addr}")
        return list(hosts.values())


def print_hosts() -> None:
    async def find_hosts() -> List[Reflex]:
        beacon = await Beacon.connect()
        hosts = await beacon.find_hosts()
        beacon.close()
        return hosts

    for host in asyncio.run(find_hosts()):
        print(f"MAC\tIP\tUptime")
        print(f"{host.mac}\t{host.addr}\t{host.info.uptime} sec")


if __name__ == "__main__":
    print_hosts()
