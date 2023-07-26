from __future__ import annotations
from typing import List

from pathlib import Path
from dataclasses import dataclass
from subprocess import run, PIPE
import shutil

from .paths import HOSTS_PATH
from mothership.hosts import Host
from mothership.config import Config


@dataclass
class _HostDirs:
    merged: Path
    diff: Path
    work: Path

    @staticmethod
    def make(host: Host) -> _HostDirs:
        merged = host.path
        path = merged.parent
        path.mkdir(exist_ok=True)
        diff, work = path / "diff", path / "work"
        for p in [merged, diff, work]:
            p.mkdir(exist_ok=True)
        return _HostDirs(merged, diff, work)


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

    def _fill_host(self, host: Host) -> _HostDirs:
        print(f"Overlayfs: Filling host {host.mac} data")
        host_dirs = _HostDirs.make(host)
        for rel_path, contents in host.files.items():
            path = host_dirs.diff / rel_path.relative_to(Path("/"))
            path.parent.mkdir(exist_ok=True, parents=True)
            print(path, contents)
            with open(path, "w") as f:
                f.write(contents)
        return host_dirs

    def _mount_host(self, host: Host) -> None:
        hd = self._fill_host(host)

        if host.base is None:
            return

        lower = ":".join([str(p) for p in host.base.branch()])

        print(f"Overlayfs: Mounting host {host.mac}")
        run(
            [
                *["mount", "-t", "overlay", "overlay"],
                *["-o", f"lowerdir={lower},upperdir={hd.diff},workdir={hd.work}"],
                *["-o", "nfs_export=on"],
                *["-o", "index=on"],
                *["-o", "redirect_dir=nofollow"],
                hd.merged,
            ],
            check=True,
        )

    def mount(self, config: Config) -> None:
        print(f"Overlayfs: Mounting all")

        old = Overlayfs._mounted()
        paths = [d.path for d in config.hosts if d.base is not None]

        for path in set(old).difference(paths):
            run(["umount", path], check=True)

        HOSTS_PATH.mkdir(exist_ok=True)
        for dev in config.hosts:
            if dev.path not in old:
                self._mount_host(dev)

        new = Overlayfs._mounted()
        assert len(set(new).symmetric_difference(paths)) == 0

    def unmount(self) -> None:
        print(f"Overlayfs: Unmounting all")

        for path in Overlayfs._mounted():
            run(["umount", path], check=True)

    def clear(self) -> None:
        print(f"Overlayfs: Removing all hosts data")
        shutil.rmtree(HOSTS_PATH)

    def fill(self, config: Config) -> None:
        HOSTS_PATH.mkdir(exist_ok=True)
        for host in config.hosts:
            self._fill_host(host)
