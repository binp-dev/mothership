from __future__ import annotations
from typing import Any, Optional, List, Dict, Type

import asyncio
from pyepics_asyncio import Pv

from mothership.hosts import Host, Status, HostStatus
from mothership.beacon import Reflex


class Ioc(Host):
    def __init__(self, *args: Any, prefix: str, **kws: Any) -> None:
        super().__init__(*args, **kws)
        self.prefix = prefix

    @classmethod
    def status_classes(cls) -> List[Type[Status]]:
        return [_IocStatus, *super().status_classes()]

    def dump(self) -> Dict[str, Any]:
        return {
            **super().dump(),
            "ioc": {"prefix": self.prefix},
        }


class _IocStatus(HostStatus[Ioc]):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)

        self.version: Optional[str] = None
        self.build_date: Optional[str] = None

    async def update(self, reflex: Reflex, force: bool = True) -> None:
        await super().update(reflex, force=force)

        try:
            async with asyncio.timeout(4):
                self.version = await (
                    await Pv.connect(f"{self.host.prefix}Version")
                ).get()
                # self.build_date = await (
                #    await Pv.connect(f"{self.host.prefix}BuildDate")
                # ).get()
        except TimeoutError:
            self.version = None
            # self.build_date = None

    def dump(self) -> Dict[str, Any]:
        data = super().dump()
        if self.version is not None:
            data["ioc"] = {
                "version": self.version,
                # "build_date": self.build_date,
            }
        return data
