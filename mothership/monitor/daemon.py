from __future__ import annotations
from typing import Any, Optional, Dict, Callable, Awaitable

from dataclasses import dataclass
import traceback

import asyncio

from mothership.hosts import Mac, Host, Status, OrphanStatus
from mothership.beacon import Beacon, Reflex
from mothership.config import Config

UPDATE_TIMEOUT = 10


@dataclass
class Entry:
    config: Optional[Host]
    status: Optional[Status] = None
    force_update: bool = True

    def dump(self) -> Dict[str, Any]:
        return {
            "config": self.config.dump() if self.config is not None else None,
            "status": self.status.dump() if self.status is not None else None,
        }


class Daemon:
    def __init__(
        self,
        config: Config,
        notify: Optional[Callable[[], Awaitable[None]]],
    ) -> None:
        self.beacon: Beacon
        self.hosts = {hc.mac: Entry(hc) for hc in config.hosts}
        self.notify = notify

    async def run(self) -> None:
        print(f"Starting daemon")
        self.beacon = await Beacon.connect()
        await self._scan_task()

    async def _scan_task(self) -> None:
        period = 10
        while True:
            print(f"Scanning ...")
            discovered = await self.beacon.find_hosts()
            print(f"Found {len(discovered)} hosts")

            await asyncio.gather(*[self._update_host(reflex) for reflex in discovered])

            if self.notify is not None:
                await self.notify()
            await asyncio.sleep(period)

    async def _update_host(self, reflex: Reflex) -> None:
        key = Mac(reflex.mac)
        if key not in self.hosts:
            self.hosts[key] = Entry(None)
        host = self.hosts[key]

        if host.status is None:
            if host.config is not None:
                host.status = host.config.new_status(reflex)
            else:
                host.status = OrphanStatus(reflex)

        try:
            async with asyncio.timeout(UPDATE_TIMEOUT):
                await host.status.update(reflex, force=host.force_update)
        except Exception:
            host.status.error = traceback.format_exc()
            print(
                f"Error while updating host '{reflex.mac} ({reflex.addr})' status:\n{host.status.error}"
            )
        else:
            host.status.error = None
            host.force_update = False

    def reboot(self, mac: Mac) -> None:
        print(f"Rebooting host {mac}")
        host = self.hosts[mac]
        assert host.status is not None
        self.beacon.reboot(host.status.addr)

    def reboot_all(self) -> None:
        print("Rebooting all hosts")
        self.beacon.reboot("255.255.255.255")

    def update(self, mac: Mac) -> None:
        self.hosts[mac].force_update = True

    def update_all(self) -> None:
        for host in self.hosts.values():
            host.force_update = True

    def dump_hosts(self) -> Dict[str, Any]:
        return {str(mac): host.dump() for mac, host in self.hosts.items()}
