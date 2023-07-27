from __future__ import annotations
from typing import Any, Optional, List, Dict, Type

import hashlib

import asyncssh

from mothership.hosts import Host, Status, HostStatus
from mothership.beacon import Reflex


class Nand(Host):
    def __init__(
        self,
        *args: Any,
        bootloader: Optional[str] = None,
        fw_env_hash: Optional[str] = None,
        **kws: Any,
    ) -> None:
        super().__init__(*args, **kws)
        self.bootloader = bootloader
        self.fw_env_hash = fw_env_hash

    @classmethod
    def status_classes(cls) -> List[Type[Status]]:
        return [_NandStatus, *super().status_classes()]

    def dump(self) -> Dict[str, Any]:
        return {
            **super().dump(),
            "nand": {
                **(
                    {"bootloader": self.bootloader}
                    if self.bootloader is not None
                    else {}
                ),
                **(
                    {"fw_env_hash": self.fw_env_hash}
                    if self.fw_env_hash is not None
                    else {}
                ),
            },
        }


class _NandStatus(HostStatus[Nand]):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.nand_read = False
        self.bootloader: Optional[str] = None
        self.fw_env_hash: Optional[str] = None

    async def update(self, reflex: Reflex, force: bool = True) -> None:
        old_boot = self.boot

        await super().update(reflex, force=force)

        if force or (self.boot - old_boot).total_seconds() > 10.0:
            self.nand_read = False

        if not self.nand_read:
            print(f"Reading NAND of '{self.host.mac}'")
            async with asyncssh.connect(
                self.addr,
                username="root",
                password="root",
                known_hosts=None,
                encoding="utf-8",
            ) as conn:
                result = await conn.run(
                    "nanddump --length 100000 --quiet /dev/mtd1 | strings | grep U-Boot",
                    check=True,
                )
                self.bootloader = result.stdout.split("\n")[0]

                result = await conn.run("fw_printenv", check=True)
                if len(result.stderr) == 0:
                    self.fw_env_hash = hashlib.sha256(
                        result.stdout.encode()
                    ).hexdigest()
                else:
                    if "Bad CRC" in result.stderr:
                        self.fw_env_hash = "Bad CRC"
                    else:
                        self.fw_env_hash = "Unknown error"

            self.nand_read = True

    def dump(self) -> Dict[str, Any]:
        data = super().dump()
        if self.nand_read:
            data["nand"] = {
                **(
                    {"bootloader": self.bootloader}
                    if self.bootloader is not None
                    else {}
                ),
                **(
                    {"fw_env_hash": self.fw_env_hash}
                    if self.fw_env_hash is not None
                    else {}
                ),
            }
        return data
