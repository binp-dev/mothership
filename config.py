from pathlib import PurePosixPath as Path

from mothership.hosts import Mac, Base, Host

debian = Base("debian")
tornado = Base("tornado", debian)
skifio = Base("skifio", tornado)

hosts = [
    Host(
        Mac("f8:dc:7a:46:04:58"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=tornado0\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1b:34"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc13\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:42"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc14\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:60"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc15\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:9c"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc16\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:a6"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc17\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:cc"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc18\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:de"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc19\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e0"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc20\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e2"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc21\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e4"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc22\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e6"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc23\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:e8"),
        base=skifio,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc24\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:ec"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc25\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:ee"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc26\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:f2"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc27\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1c:f4"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc28\n"},
    ),
    Host(
        Mac("f8:dc:7a:a4:1d:16"),
        base=tornado,
        files={Path("/opt/env.cmd"): "export DEV_NAME=mpsc29\n"},
    ),
]
