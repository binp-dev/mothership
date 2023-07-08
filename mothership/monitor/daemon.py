from __future__ import annotations
from typing import Any, Optional, Sequence, Dict

from dataclasses import dataclass
from datetime import datetime, timedelta

import asyncio

from mothership.config import Config, Host, Mac
from mothership.discover import find_hosts


@dataclass
class Info:
    addr: str
    boot: datetime
    online: datetime

    def flatten(self) -> Dict[str, Any]:
        return {
            "addr": self.addr,
            "boot": int(self.boot.timestamp()),
            "online": int(self.online.timestamp()),
        }


@dataclass
class HostInfo:
    host: Optional[Host]
    info: Optional[Info] = None

    def flatten(self) -> Dict[str, Any]:
        return {
            "host": {
                "mac": str(self.host.mac),
                **({"base": self.host.base.name} if self.host.base is not None else {}),
                **({"addr": self.host.addr} if self.host.addr is not None else {}),
            }
            if self.host is not None
            else None,
            "info": self.info.flatten() if self.info is not None else None,
        }


class Daemon:
    def __init__(self, config: Config) -> None:
        self.hosts = {host.mac: HostInfo(host) for host in config.hosts}

    async def run(self) -> None:
        asyncio.create_task(self._scan_task())
        print(f"Daemon started")

    async def _scan_task(self) -> None:
        period = 30
        while True:
            print(f"Scanning ...")
            discovered = await find_hosts()
            print(f"Found {len(discovered)} hosts")
            for mac, info in discovered.items():
                key = Mac(mac)
                if key not in self.hosts:
                    self.hosts[key] = HostInfo(None)
                host = self.hosts[key]
                now = datetime.now()
                host.info = Info(
                    addr=info.addr,
                    online=now,
                    boot=now - timedelta(seconds=info.uptime),
                )
            await asyncio.sleep(period)

    def flat_hosts(self) -> Dict[str, Any]:
        return {str(mac): host.flatten() for mac, host in self.hosts.items()}
