from __future__ import annotations
from typing import Any, Optional, Sequence, Dict

from dataclasses import dataclass
from datetime import datetime, timedelta

import asyncio

from mothership.config import Config, Host as HostConfig, Mac
from mothership.discover import find_hosts


@dataclass
class Status:
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
class Host:
    config: Optional[HostConfig]
    status: Optional[Status] = None

    def flatten(self) -> Dict[str, Any]:
        return {
            "config": {
                "mac": str(self.config.mac),
                **(
                    {"base": self.config.base.name}
                    if self.config.base is not None
                    else {}
                ),
                **({"addr": self.config.addr} if self.config.addr is not None else {}),
            }
            if self.config is not None
            else None,
            "status": self.status.flatten() if self.status is not None else None,
        }


class Daemon:
    def __init__(self, config: Config) -> None:
        self.hosts = {hc.mac: Host(hc) for hc in config.hosts}

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
                    self.hosts[key] = Host(None)
                host = self.hosts[key]
                now = datetime.now()
                host.status = Status(
                    addr=info.addr,
                    online=now,
                    boot=now - timedelta(seconds=info.uptime),
                )
            await asyncio.sleep(period)

    def flat_hosts(self) -> Dict[str, Any]:
        return {str(mac): host.flatten() for mac, host in self.hosts.items()}
