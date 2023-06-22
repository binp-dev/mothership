from __future__ import annotations
from typing import List

from pathlib import Path
from argparse import ArgumentParser
import toml

from .config import Config


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="Mothership", description="PS controller orchestration"
    )
    parser.add_argument("config_path", type=str, help="Path to config.toml")
    args = parser.parse_args()
    with open(Path(args.config_path), "r") as f:
        config = Config(**toml.load(f))
    print(config)

    print("Mothership service started")
    try:
        pass
    finally:
        print("Mothership service stopped")
