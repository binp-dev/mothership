#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <sys/sysinfo.h>

static const int PING_RATE = 30; // seconds
static const size_t BUFFER_LEN = 0x100;

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Watchdog device required");
        return 1;
    }

    char *wd_file = argv[1];
    int wd = open(wd_file, O_WRONLY);
    if (wd < 0)
    {
        printf("Failed to open %s: %s\n", wd_file, strerror(errno));
        return 2;
    }

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        printf("Failed to create socket: %s\n", strerror(errno));
        return 3;
    }
    struct sockaddr_in local_addr;
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;
    local_addr.sin_port = htons(9696);
    int one = 1;
    if (bind(sock, (struct sockaddr *)&local_addr, sizeof(local_addr)) != 0 && //
        setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &one, sizeof(one)) != 0)
    {
        printf("Failed to configure socket: %s\n", strerror(errno));
        return 3;
    }

    printf("Watchdog started\n");

    uint8_t buffer[BUFFER_LEN];
    struct pollfd pfd;
    pfd.fd = sock;
    pfd.events = POLLIN;
    for (;;)
    {
        int dummy;
        if (ioctl(wd, WDIOC_KEEPALIVE, &dummy) != 0)
        {
            printf("Watchdog ioctl error: %s\n", strerror(errno));
            return 4;
        }
        // printf("Watchdog keep alive\n");

        pfd.revents = 0;
        int ready = poll(&pfd, 1, PING_RATE * 1000);
        if (ready < 0)
        {
            printf("Socket poll error: %s\n", strerror(errno));
            return 5;
        }
        if (ready > 0)
        {
            if ((pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) != 0)
            {
                printf("Bad socket events: %d\n", (int)pfd.revents);
                return 5;
            }
            if (pfd.revents & POLLIN)
            {
                struct sockaddr_in addr;
                socklen_t addr_len = sizeof(addr);
                int len = recvfrom(sock, (char *)buffer, BUFFER_LEN, MSG_DONTWAIT, (struct sockaddr *)&addr, &addr_len);
                if (len < 0)
                {
                    printf("Error receiving message: %s\n", strerror(errno));
                    return 5;
                }
                // printf("Message received from: %s:%d\n", inet_ntoa(addr.sin_addr), (int)ntohs(addr.sin_port));

                if (len < 2 || buffer[0] != 0x96)
                {
                    printf("Bad message format\n");
                }
                else
                {
                    int code = buffer[1];
                    if (code == 0xEC)
                    {
                        struct sysinfo info;
                        if (sysinfo(&info) != 0)
                        {
                            printf("Error getting sysinfo: %s\n", strerror(errno));
                        }
                        else
                        {
                            uint32_t uptime = htonl((uint32_t)info.uptime);
                            buffer[0] = 0x96;
                            buffer[1] = 0xCE;
                            memcpy(buffer + 2, &uptime, 4);
                            len = 2 + 4;
                            if (sendto(sock, buffer, len, 0, (struct sockaddr *)&addr, addr_len) != len)
                            {
                                printf("Error sending message %s\n", strerror(errno));
                            }
                        }
                    }
                    else if (code == 0xB0)
                    {
                        printf("Reset now\n");
                        fflush(stdout);

                        int wd_timeout = 1;
                        if (ioctl(wd, WDIOC_SETTIMEOUT, &wd_timeout) != 0)
                        {
                            printf("Error setting watchdog timeout to zero: %s\n", strerror(errno));
                            return 4;
                        }

                        return 0;
                    }
                }
            }
        }
    }

    return 0;
}
