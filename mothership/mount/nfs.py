from __future__ import annotations
from typing import List

from pathlib import Path
from subprocess import run

from mothership.tree import Device

EXPORTS_PATH = Path("/etc/exports.d/mothership.exports")


class Nfs:
    def refresh(self) -> None:
        run(["exportfs", "-ra"], check=True)

    def export(self, devices: List[Device]) -> None:
        print("Nfs: export all")
        EXPORTS_PATH.parent.mkdir(exist_ok=True)
        with open(EXPORTS_PATH, "w") as f:
            for dev in devices:
                f.write(f"{dev.path} *(rw,sync,no_subtree_check,no_root_squash)\n")
        self.refresh()

    def unexport(self) -> None:
        print("Nfs: unexport all")
        if EXPORTS_PATH.exists():
            EXPORTS_PATH.unlink()
        self.refresh()
