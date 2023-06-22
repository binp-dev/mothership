from __future__ import annotations

from pathlib import Path
from time import sleep
from argparse import ArgumentParser
import toml

from .config import Config, FS_PATH
from .nfs import Nfs
from .overlayfs import Overlayfs


parser = ArgumentParser(prog="Mothership", description="PS controller orchestration")
parser.add_argument("config_path", type=str, help="Path to config.toml")
args = parser.parse_args()
with open(Path(args.config_path), "r") as f:
    config = Config(**toml.load(f))
print(config)

assert FS_PATH.exists(), f"Base FS directory not found at {FS_PATH}"
nfs = Nfs()
overlayfs = Overlayfs()

try:
    print("Starting mothership service")
    nfs.unexport()
    overlayfs.mount(config)
    nfs.export(config)

    print("Mothership service started")
    while True:
        sleep(0.1)

except Exception as e:
    print("Error:", e)
    raise

finally:
    nfs.unexport()
    overlayfs.unmount()
    print("Mothership service stopped")
