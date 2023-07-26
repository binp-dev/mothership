from __future__ import annotations

from pathlib import Path
from subprocess import run

from mothership.config import Config

EXPORTS_PATH = Path("/etc/exports.d/mothership.exports")


class Nfs:
    def refresh(self) -> None:
        run(["exportfs", "-ra"], check=True)

    def export(self, config: Config) -> None:
        print("Nfs: export all")
        EXPORTS_PATH.parent.mkdir(exist_ok=True)
        with open(EXPORTS_PATH, "w") as f:
            for host in config.hosts:
                fsid = "aaaa" + str(host.mac).replace(":", "") + ("0" * 16)
                f.write(
                    f"{host.path} *(rw,sync,no_subtree_check,no_root_squash,fsid={fsid})\n"
                )
        self.refresh()

    def unexport(self) -> None:
        print("Nfs: unexport all")
        if EXPORTS_PATH.exists():
            EXPORTS_PATH.unlink()
        self.refresh()
