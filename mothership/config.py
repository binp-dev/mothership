from __future__ import annotations
from typing import Any, List, Dict

from pathlib import Path, PurePosixPath
from dataclasses import dataclass, field

FS_PATH = Path("/srv/nfs")
BASES_PATH = FS_PATH / "bases"
HOSTS_PATH = FS_PATH / "hosts"


class Mac:
    def __init__(self, addr: str) -> None:
        parts = addr.split(":")
        assert len(parts) == 6
        self.bytes = bytes([int(p, base=16) for p in parts])

    def __hash__(self) -> int:
        return hash(self.bytes)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Mac):
            raise TypeError(f"`other` must be {Mac}, not {type(other)}")
        return self.bytes == other.bytes

    def __str__(self) -> str:
        return ":".join([f"{b:02x}" for b in self.bytes])

    def __repr__(self) -> str:
        return f"Mac({str(self)})"


@dataclass
class Base:
    name: str
    parent: Base | None = None
    _path: Path | None = None

    @property
    def path(self) -> Path:
        if self._path is not None:
            return self._path
        else:
            return BASES_PATH / self.name

    def branch(self) -> List[Path]:
        if self.parent is not None:
            base = self.parent.branch()
        else:
            base = []
        return [*base, self.path]


@dataclass
class Host:
    mac: Mac
    addr: str | None = None
    base: Base | None = None
    files: Dict[PurePosixPath, str] = field(default_factory=dict)

    @property
    def path(self) -> Path:
        return HOSTS_PATH / str(self.mac) / "merged"


@dataclass
class Config:
    hosts: List[Host]

    @staticmethod
    def load(path: Path) -> Config:
        import importlib.util

        spec = importlib.util.spec_from_file_location("config", path)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        return Config(module.hosts)
