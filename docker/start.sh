#!/bin/bash

function setting {
    touch /setting.lock

    ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
    echo $TZ > /etc/timezone
}
if [ ! -f /setting.lock ]; then
	setting
fi
chown -R ${PUID}:${PGID} /opt
umask ${UMASK}

cat /opt/docker/EmbyChineseNameSynchronous
echo "以PUID=${PUID}，PGID=${PGID}的身份启动程序,umask=${UMASK}"
cd /opt
exec su-exec ${PUID}:${PGID} python3 main.py
