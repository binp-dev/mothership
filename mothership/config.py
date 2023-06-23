from __future__ import annotations
from typing import Dict

from pydantic.dataclasses import dataclass


@dataclass
class Base:
    parent: str | None = None
    path: str | None = None


@dataclass
class Host:
    base: str
    addr: str | None = None


@dataclass
class Config:
    bases: Dict[str, Base]
    hosts: Dict[str, Host]
