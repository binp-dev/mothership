from __future__ import annotations
from typing import List

from pydantic.dataclasses import dataclass


@dataclass
class Device:
    mac: str
    ip: str | None = None


@dataclass
class Config:
    devices: List[Device]
