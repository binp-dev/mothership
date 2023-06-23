#!/usr/bin/bash

scp watchdog.py root@$1:/opt/ && \
scp watchdog.service root@$1:/etc/systemd/system/ && \
ssh root@$1 "systemctl enable watchdog && systemctl restart watchdog" && \
echo "Done!"
