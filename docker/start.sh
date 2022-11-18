#!/bin/bash

# 初始设置
function setting {
    touch /setting.lock

    ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
    echo $TZ > /etc/timezone
}
if [ ! -f /setting.lock ]; then
	setting
fi

# 自动更新
if [ "$ECNS_AUTO_UPDATE" = "true" ]; then
    if [ ! -s /tmp/requirement.txt.sha256sum ]; then
        sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
    fi
    if [ ! -s /tmp/package_list.txt.sha256sum ]; then
        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
    fi
    echo "更新程序..."
    if [ ! -d /tmp/config ]; then
        mkdir -p /tmp/config
    fi
    rm -rf /tmp/config/*
    cp -r /ecns/config/* /tmp/config
    git remote set-url origin ${REPO_URL} &>/dev/null
    git clean -dffx
    git reset --hard HEAD
    git pull
    if [ $? -eq 0 ]; then
        echo "更新成功..."
        rm -rf /ecns/config/*
        cp -r /tmp/config/* /ecns/config
        hash_old=$(cat /tmp/requirement.txt.sha256sum)
        hash_new=$(sha256sum requirement.txt)
        if [ "$hash_old" != "$hash_new" ]; then
            echo "检测到requirement.txt有变化，重新安装依赖..."
            pip install --upgrade pip setuptools wheel
            pip install -r requirement.txt
            if [ $? -ne 0 ]; then
                echo "无法安装依赖，请更新镜像..."
            else
                echo "依赖安装成功..."
                sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
                hash_old=$(cat /tmp/package_list.txt.sha256sum)
                hash_new=$(sha256sum docker/package_list.txt)
                if [ "$hash_old" != "$hash_new" ]; then
                    echo "检测到package_list.txt有变化，更新软件包..."
                    apk add --no-cache $(echo $(cat docker/package_list.txt))
                    if [ $? -ne 0 ]; then
                        echo "无法更新软件包，请更新镜像..."
                    else
                        echo "软件包安装成功..."
                        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
                    fi
                fi
            fi
        fi
    else
        echo "更新失败，继续使用旧的程序来启动..."
    fi
else
    echo "程序自动升级已关闭，如需自动升级请在创建容器时设置环境变量：ECNS_AUTO_UPDATE=true"
fi

# 权限设置
chown -R ${PUID}:${PGID} ${WORK_DIR}
chmod +x /ecns/docker/start.sh
umask ${UMASK}

# 启动
echo -e "——————————————————————————————————————————————————————————
        _____  ____  _   _  ____  
        | ____|/ ___|| \ | |/ ___| 
        |  _| | |    |  \| |\___ \ 
        | |___| |___ | |\  | ___) |
        |_____|\____||_| \_||____/ 

以PUID=${PUID}，PGID=${PGID}，Umask=${UMASK}的身份启动程序

——————————————————————————————————————————————————————————"
echo

exec su-exec ${PUID}:${PGID} python3 main.py
