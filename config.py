from pathlib import PurePosixPath as Path

from mothership.config import Mac, Base, Host

debian = Base("debian")
tornado = Base("tornado", debian)
skifio = Base("skifio", tornado)

hosts = [
    Host(
        Mac("f8:dc:7a:46:04:58"),
        base=skifio,
        files={Path("/opt/env.cmd"): 'epicsEnvSet("NAME","tornado0")\n'},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e8"),
        base=skifio,
        files={Path("/opt/env.cmd"): 'epicsEnvSet("NAME","mpsc25")\n'},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:f2"),
        base=skifio,
        files={Path("/opt/env.cmd"): 'epicsEnvSet("NAME","mpsc27")\n'},
    ),
]
