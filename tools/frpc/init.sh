#!/bin/bash
USER_HOME=$(eval echo ~$USER)
sed -i "s|\$HOME|$USER_HOME|g" "frp-client.service"
sed -i "s|\$HOME|$USER_HOME|g" "run.sh"
systemctl stop frp-client.service
cp frp-client.service /etc/systemd/system/frp-client.service
systemctl start frp-client.service
systemctl enable frp-client.service
systemctl daemon-reload
