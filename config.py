from pathlib import PurePosixPath as Path

from mothership.hosts import Mac, Base, Host
from mothership.hosts.nand import Nand
from mothership.hosts.ioc import Ioc

debian = Base("debian")
tornado = Base("tornado", debian)
skifio = Base("skifio", tornado)


class Skifio(Ioc, Nand):
    def __init__(self, mac: Mac, name: str) -> None:
        super().__init__(
            mac,
            base=skifio,
            files={Path("/opt/env.sh"): f"export DEV_NAME={name}\n"},
            bootloader="U-Boot SPL 2020.04-49381-ged2486e7d2 (Jul 27 2023 - 10:33:36 +0700)",
            fw_env_hash="d73fc4f676c7d1388cb5da50a13f02af54bf0f1b5683abdff9e62248a8c4d91a",
            prefix=f"{name}:",
        )
        self.name = name


hosts = [
    Host(Mac("f8:dc:7a:46:04:58"), base=tornado),
    Skifio(Mac("f8:dc:7a:a4:1b:34"), "mpsc13"),
    Skifio(Mac("f8:dc:7a:a4:1c:42"), "mpsc14"),
    Skifio(Mac("f8:dc:7a:a4:1c:60"), "mpsc15"),
    Skifio(Mac("f8:dc:7a:a4:1c:9c"), "mpsc16"),
    Skifio(Mac("f8:dc:7a:a4:1c:a6"), "mpsc17"),
    Skifio(Mac("f8:dc:7a:a4:1c:cc"), "mpsc18"),
    Skifio(Mac("f8:dc:7a:a4:1c:de"), "mpsc19"),
    Skifio(Mac("f8:dc:7a:a4:1c:e0"), "mpsc20"),
    Skifio(Mac("f8:dc:7a:a4:1c:e2"), "mpsc21"),
    Skifio(Mac("f8:dc:7a:a4:1c:e4"), "mpsc22"),
    Skifio(Mac("f8:dc:7a:a4:1c:e6"), "mpsc23"),
    Skifio(Mac("f8:dc:7a:a4:1c:e8"), "mpsc24"),
    Skifio(Mac("f8:dc:7a:a4:1c:ec"), "mpsc25"),
    Skifio(Mac("f8:dc:7a:a4:1c:ee"), "mpsc26"),
    Skifio(Mac("f8:dc:7a:a4:1c:f2"), "mpsc27"),
    Skifio(Mac("f8:dc:7a:a4:1c:f4"), "mpsc28"),
    Skifio(Mac("f8:dc:7a:a4:1d:16"), "mpsc29"),
]
