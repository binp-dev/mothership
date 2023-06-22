from __future__ import annotations
from typing import List

from pathlib import Path
from subprocess import run, PIPE

from .config import Config, Device, FS_PATH, HOSTS_PATH, COMMON_PATH


class Overlayfs:
    @staticmethod
    def _mounted() -> List[Path]:
        points = []
        output = run(["mount"], stdout=PIPE, text=True, check=True).stdout
        for line in output.strip().split("\n"):
            type, _on, path = line.split(" ")[:3]
            assert _on == "on"
            if type == "overlay" and HOSTS_PATH in Path(path).parents:
                points.append(Path(path))
        return points

    def _mount_single(self, device: Device) -> None:
        print(f"Overlayfs: Mounting device {device.mac}")

        common = COMMON_PATH
        assert common.exists(), f"Common FS not found at {common}"

        path = device.path
        path.mkdir(exist_ok=True)
        merged = device.rootfs_path
        diff, work = path / "diff", path / "work"
        for p in [merged, diff, work]:
            p.mkdir(exist_ok=True)

        run(
            [
                *["mount", "-t", "overlay", "overlay"],
                *["-o", f"lowerdir={common},upperdir={diff},workdir={work}"],
                *["-o", "nfs_export=on"],
                *["-o", "index=on"],
                merged,
            ],
            check=True,
        )

    def mount(self, config: Config) -> None:
        print(f"Overlayfs: Mounting all")

        old = Overlayfs._mounted()
        paths = [d.rootfs_path for d in config.devices]

        for path in set(old).difference(paths):
            run(["umount", path], check=True)

        HOSTS_PATH.mkdir(exist_ok=True, parents=True)
        for dev in config.devices:
            if dev.rootfs_path not in old:
                self._mount_single(dev)

        new = Overlayfs._mounted()
        assert len(set(new).symmetric_difference(paths)) == 0

    def unmount(self) -> None:
        print(f"Overlayfs: Unmounting all")

        for path in Overlayfs._mounted():
            run(["umount", path], check=True)
