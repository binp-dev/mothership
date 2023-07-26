from __future__ import annotations
from typing import Any, Optional, Dict

from dataclasses import dataclass

from mothership.hosts import Host, Status
from mothership.beacon import Reflex


class _NandStatus(Status):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.nand_read = False
        self.bootloader: Optional[str] = None
        self.fw_env_hash: Optional[str] = None

    async def update(self, reflex: Reflex) -> None:
        old_boot = self.boot
        await super().update(reflex)
        if old_boot < self.boot:
            self.nand_read = False
        if not self.nand_read:
            self.bootloader = "U-boot"
            self.fw_env_hash = "deadbeef"
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


@dataclass
class Nand(Host):
    Status = _NandStatus

    bootloader: Optional[str] = None
    fw_env_hash: Optional[str] = None

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
