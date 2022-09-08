#!/bin/bash

function setting {

touch /setting.lock

ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
echo $TZ > /etc/timezone

mkdir -p /opt/config

if [ ! -f /opt/config/config.yaml ]; then
    cp /home/config.yaml /opt/config/config.yaml
fi

if [ ! -f /opt/config/data.db ]; then
    cp /home/data.db /opt/config/data.db
fi

}

if [ ! -f /setting.lock ]; then
	setting
fi

cd /opt
python3 main.py
