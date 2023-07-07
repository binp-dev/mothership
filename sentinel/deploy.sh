#!/usr/bin/bash

if [[ -z $1 ]] then echo "Usage: ./deploy.sh <host-addr>"; exit 1; fi;

ssh root@$1 "mkdir -p /opt/sentinel/" && \
scp main.c Makefile root@$1:/opt/sentinel/ && \
ssh root@$1 "cd /opt/sentinel/ && make" && \
scp sentinel.service root@$1:/etc/systemd/system/ && \
ssh root@$1 "systemctl daemon-reload" && \
ssh root@$1 "systemctl enable sentinel && systemctl restart sentinel" && \
echo "Done!"
