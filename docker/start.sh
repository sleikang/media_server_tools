#!/bin/bash

Green="\033[32m"
Font="\033[0m"
Red="\033[31m" 

# 初始设置
function setting {
    touch /setting.lock

    ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
    echo $TZ > /etc/timezone

    # 兼容旧config文件路径
    if [ -d /opt/config ] && [ ! -d /config ]; then
        echo -e "${Green}使用v1.x版本config路径配置${Font}"
        rm -rf /config
        ln -s /opt/config /
    else
        mkdir -p /config
    fi
}
if [ ! -f /setting.lock ]; then
	setting
fi

# 自动更新
function app_update {
    echo -e "${Green}更新程序...${Font}"
    git remote set-url origin ${REPO_URL} &>/dev/null
    git clean -dffx
    git reset --hard HEAD
    git pull
}

function requirement_update {
    echo -e "${Green}检测到requirement.txt有变化，重新安装依赖...${Font}"
    pip install --upgrade pip setuptools wheel
    pip install -r requirement.txt
}

function package_list_update {
    echo -e "${Green}检测到package_list.txt有变化，更新软件包...${Font}"
    apk add --no-cache $(echo $(cat docker/package_list.txt))
}

if [ "${MediaServerTools_AUTO_UPDATE}" = "true" ]; then
    if [ ! -s /tmp/requirement.txt.sha256sum ]; then
        sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
    fi
    if [ ! -s /tmp/package_list.txt.sha256sum ]; then
        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
    fi
    app_update
    if [ $? -eq 0 ]; then
        echo -e "${Green}更新成功...${Font}"
        hash_old=$(cat /tmp/requirement.txt.sha256sum)
        hash_new=$(sha256sum requirement.txt)
        if [ "$hash_old" != "$hash_new" ]; then
            requirement_update
            if [ $? -ne 0 ]; then
                echo -e "${Red}无法安装依赖，请更新镜像...${Font}"
            else
                echo -e "${Green}依赖安装成功...${Font}"
                sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
                hash_old=$(cat /tmp/package_list.txt.sha256sum)
                hash_new=$(sha256sum docker/package_list.txt)
                if [ "$hash_old" != "$hash_new" ]; then
                    package_list_update
                    if [ $? -ne 0 ]; then
                        echo -e "${Red}无法更新软件包，请更新镜像...${Font}"
                    else
                        echo -e "${Green}软件包安装成功...${Font}"
                        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
                    fi
                fi
            fi
        fi
    else
        echo -e "${Red}更新失败，继续使用旧的程序来启动...${Font}"
    fi
else
    echo -e "${Green}程序自动升级已关闭，如需自动升级请在创建容器时设置环境变量：ECNS_AUTO_UPDATE=true${Font}"
fi

# 权限设置
chown -R ${PUID}:${PGID} ${WORK_DIR}

if [[ "$(stat -c '%u' ${EMBYTOOLS_CONFIG})" != "${PUID}" ]] || [[ "$(stat -c '%g' ${EMBYTOOLS_CONFIG})" != "${PGID}" ]]; then
    chown ${PUID}:${PGID} ${EMBYTOOLS_CONFIG}
fi

if [[ "$(stat -c '%A' ${WORK_DIR}/docker/start.sh)" != "-rwxr-xr-x" ]]; then
chmod 755 ${WORK_DIR}/docker/start.sh
fi

umask ${UMASK}

# 启动
echo -e "————————————————————————————————————————————————————————————————————————————————————————"
cat ${WORK_DIR}/docker/MediaServerTools
echo -e "

${Green}以PUID=${PUID}，PGID=${PGID}，Umask=${UMASK}的身份启动程序${Font}
———————————————————————————————————————————————————————————————————————————————————————— 

"

exec su-exec ${PUID}:${PGID} python3 main.py
