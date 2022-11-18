#!/bin/bash

function setting {
    touch /setting.lock

    ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
    echo $TZ > /etc/timezone
}
if [ ! -f /setting.lock ]; then
	setting
fi

chown -R ${PUID}:${PGID} ${WORK_DIR}
umask ${UMASK}

echo -e "——————————————————————————————————————————————————————————
        _____  ____  _   _  ____  
        | ____|/ ___|| \ | |/ ___| 
        |  _| | |    |  \| |\___ \ 
        | |___| |___ | |\  | ___) |
        |_____|\____||_| \_||____/ 

以PUID=${PUID}，PGID=${PGID}，Umask=${UMASK}的身份启动程序

——————————————————————————————————————————————————————————"
echo

cd ${WORK_DIR}

exec su-exec ${PUID}:${PGID} python3 main.py
