#!/bin/bash

function setting {

touch /setting.lock

ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
echo $TZ > /etc/timezone

}

if [ ! -f /setting.lock ]; then
	setting
fi

cd /opt
python3 main.py
