#!/bin/bash

ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
echo $TZ > /etc/timezone

function setting {

mkdir -p /opt/config
cp /home/config.yaml /opt/config/config.yaml

}

if [ ! -f /opt/config/config.yaml ]; then
	setting
fi

cd /opt
python3 main.py
