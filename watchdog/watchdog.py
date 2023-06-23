#!/usr/bin/env python3

import time


lock = open("/var/watchdog.lock", "w")

failures = 0
while True:
    with open("/dev/watchdog0", "w") as watchdog:
        watchdog.write("1\n")

    time.sleep(30)

    try:
        lock.seek(0)
        lock.write("1\n")
        lock.flush()
    except RuntimeError:
        failures += 1
        if failures >= 2:
            raise
    else:
        failures = 0
