from __future__ import annotations

from pathlib import Path
from argparse import ArgumentParser
import toml

from .config import Config, FS_PATH
from .nfs import Nfs
from .overlayfs import Overlayfs


parser = ArgumentParser(prog="Mothership", description="PS controller orchestration")
parser.add_argument(
    "command",
    type=str,
    choices=["up", "down"],
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

assert FS_PATH.exists(), f"Base FS directory not found at {FS_PATH}"
nfs = Nfs()
overlayfs = Overlayfs()

if args.command == "up":
    assert args.config is not None
    with open(Path(args.config), "r") as f:
        config = Config(**toml.load(f))
    print(config)

    nfs.unexport()
    overlayfs.mount(config)
    nfs.export(config)

elif args.command == "down":
    nfs.unexport()
    overlayfs.unmount()
