from __future__ import annotations
from typing import List

from pathlib import Path
from dataclasses import dataclass

from mothership.hosts import Host


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
