from __future__ import annotations
from typing import List

from pathlib import Path
from pydantic.dataclasses import dataclass

FS_PATH = Path("/srv/nfs")
COMMON_PATH = FS_PATH / "common"
HOSTS_PATH = FS_PATH / "hosts"


@dataclass
class Device:
    mac: str
    ip: str | None = None

    @property
    def path(self) -> Path:
        return HOSTS_PATH / self.mac

    @property
    def rootfs_path(self) -> Path:
        return self.path / "merged"


@dataclass
class Config:
    devices: List[Device]
