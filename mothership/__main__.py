from __future__ import annotations

from argparse import ArgumentParser

from .mount.nfs import Nfs
from .mount.overlayfs import Overlayfs
from .config import Config, FS_PATH


parser = ArgumentParser(
    prog="Mothership",
    description="Netboot management for multiple devices",
)
parser.add_argument(
    "command",
    type=str,
    choices=["mount", "unmount", "clear", "fill"],
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

if args.config is not None:
    config = Config.load(args.config)
    print(config)
else:
    config = None

if args.command == "mount":
    assert config is not None
    nfs.unexport()
    overlayfs.mount(config)
    nfs.export(config)

elif args.command == "unmount":
    nfs.unexport()
    overlayfs.unmount()

elif args.command == "clear":
    overlayfs.clear()

elif args.command == "fill":
    overlayfs.fill(config)

else:
    raise KeyError(f"Unknown command: {args.command}")
