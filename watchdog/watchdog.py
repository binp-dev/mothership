#!/usr/bin/env python3

import time


def ping_watchdog() -> None:
    with open("/dev/watchdog0", "w") as watchdog:
        watchdog.write("1\n")


def check_fs() -> None:
    with open("/var/watchdog.lock", "w") as lock:
        lock.write("1\n")


failures = 0
while True:
    ping_watchdog()

    time.sleep(30)

    try:
        check_fs()
    except RuntimeError:
        failures += 1
        if failures >= 2:
            raise
