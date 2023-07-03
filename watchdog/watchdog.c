// SPDX-License-Identifier: GPL-2.0
/*
 * Watchdog Driver Test Program
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

static const unsigned int PING_RATE = 30;
static const char *const LOCK_FILE = "/var/watchdog.lock";
static const int MAX_FAILURES = 2;

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Watchdog device required");
        return 1;
    }

    char *filename = argv[1];
    int watchdog = open(filename, O_WRONLY);
    if (watchdog < 0)
    {
        printf("Failed to open %s: %s\n", filename, strerror(errno));
        return 2;
    }

    int lock = open(LOCK_FILE, O_WRONLY);
    if (lock < 0)
    {
        printf("Failed to open lock file: %s\n", LOCK_FILE, strerror(errno));
        return 3;
    }

    printf("Watchdog started\n");

    int failures = 0;
    for (;;)
    {
        int dummy;
        if (ioctl(watchdog, WDIOC_KEEPALIVE, &dummy) != 0)
        {
            printf("Watchdog ioctl error: %s\n", strerror(errno));
            return 4;
        }
        // printf("Watchdog keep alive\n");

        sleep(PING_RATE);

        if (lseek(lock, 0, SEEK_SET) == 0 //
            && write(lock, "1\n", 2) == 2 //
            && fsync(lock) == 0)
        {
            failures = 0;
        }
        else
        {
            failures += 1;
            printf("Lock file write error (%d): %s\n", failures, strerror(errno));
        }

        if (failures >= MAX_FAILURES)
        {
            printf("Failure count reached max value, exiting\n");
            return 5;
        }
    }

    return 0;
}
