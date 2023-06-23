from __future__ import annotations
from typing import List, Dict

from pathlib import Path
from dataclasses import dataclass
from graphlib import TopologicalSorter

from .config import Config

FS_PATH = Path("/srv/nfs")
BASES_PATH = FS_PATH / "bases"
HOSTS_PATH = FS_PATH / "hosts"


class Mac:
    def __init__(self, addr: str) -> None:
        parts = addr.split(":")
        assert len(parts) == 6
        self.bytes = bytes([int(p, base=16) for p in parts])

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
class Device:
    base: Base
    mac: Mac
    addr: str | None = None

    @property
    def path(self) -> Path:
        return HOSTS_PATH / str(self.mac) / "merged"


def build_tree(config: Config) -> List[Device]:
    graph: TopologicalSorter[str] = TopologicalSorter()
    for name, bcfg in config.bases.items():
        if bcfg.parent is None:
            graph.add(name)
        else:
            graph.add(name, bcfg.parent)

    bases: Dict[str, Base] = {}
    for name in graph.static_order():
        bcfg = config.bases[name]
        parent = bases[bcfg.parent] if bcfg.parent is not None else None
        path = Path(bcfg.path) if bcfg.path is not None else None
        bases[name] = Base(name, parent, path)

    devices: List[Device] = []
    for addr, host in config.hosts.items():
        devices.append(Device(bases[host.base], Mac(addr), addr=host.addr))
    return devices
