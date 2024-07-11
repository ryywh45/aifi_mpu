#!/bin/bash
systemctl stop frp-client.service
cp frp-client.service /etc/systemd/system/frp-client.service
systemctl start frp-client.service
systemctl enable frp-client.service
systemctl daemon-reload
