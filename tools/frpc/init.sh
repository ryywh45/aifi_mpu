#!/bin/bash
USER_HOME=$(eval echo ~$USER)
sed -i "s|\$HOME|$USER_HOME|g" "frp-client.service"
sed -i "s|\$HOME|$USER_HOME|g" "run.sh"
sudo systemctl stop frp-client.service
sudo cp frp-client.service /etc/systemd/system/frp-client.service
sudo systemctl start frp-client.service
sudo systemctl enable frp-client.service
sudo systemctl daemon-reload
