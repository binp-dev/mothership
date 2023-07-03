#!/usr/bin/bash

ssh root@$1 "mkdir -p /opt/watchdog/" && \
scp watchdog.c root@$1:/opt/watchdog/ && \
ssh root@$1 "cd /opt/watchdog/ && gcc watchdog.c -o watchdog" && \
scp watchdog.service root@$1:/etc/systemd/system/ && \
ssh root@$1 "systemctl daemon-reload" && \
ssh root@$1 "systemctl enable watchdog && systemctl restart watchdog" && \
echo "Done!"
