from __future__ import annotations
from typing import Self, Optional, Callable, Dict

import asyncio
from argparse import ArgumentParser

from .mount import FS_PATH, Nfs, Overlayfs
from .config import Config
from .beacon import print_hosts
from .monitor.app import App as Monitor


def command(fn: Callable[[Mothership], None]) -> Callable[[Mothership], None]:
    setattr(fn, "_is_command", True)
    return fn


class Mothership:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config
        assert FS_PATH.exists(), f"Base FS directory not found at {FS_PATH}"
        self.nfs = Nfs()
        self.overlayfs = Overlayfs()

    @classmethod
    def commands(cls) -> Dict[str, Callable[[Self], None]]:
        cmds = {}
        for name in dir(cls):
            item = getattr(cls, name)
            if hasattr(item, "_is_command"):
                cmds[name] = item
        return cmds

    def run_command(self, name: str) -> None:
        self.commands()[name](self)

    @command
    def mount(self) -> None:
        assert self.config is not None
        self.nfs.unexport()
        self.overlayfs.mount(config)
        self.nfs.export(config)

    @command
    def unmount(self) -> None:
        self.nfs.unexport()
        self.overlayfs.unmount()

    @command
    def clear(self) -> None:
        self.overlayfs.clear()

    @command
    def fill(self) -> None:
        assert self.config is not None
        self.overlayfs.fill(self.config)

    @command
    def discover(self) -> None:
        print_hosts()

    @command
    def monitor(self) -> None:
        assert self.config is not None
        asyncio.run(Monitor(config).run(("0.0.0.0", 5000)))


parser = ArgumentParser(
    prog="Mothership",
    description="Netboot management for multiple devices",
)
parser.add_argument(
    "command",
    type=str,
    choices=Mothership.commands().keys(),
    help="Command to run.",
)
parser.add_argument(
    "config",
    nargs="?",
    default=None,
    type=str,
    help="Path to config.toml",
)
args = parser.parse_args()


if args.config is not None:
    config = Config.load(args.config)
    print(config)
else:
    config = None

Mothership(config).run_command(args.command)
