#!/bin/bash

# 初始设置
function setting {
    touch /setting.lock

    ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
    echo $TZ > /etc/timezone

    # 兼容旧config文件路径
    if [ -d /opt/config ] && [ ! -d /config ]; then
        echo -e "使用v1.x版本config路径配置"
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
    echo "更新程序..."
    git remote set-url origin ${REPO_URL} &>/dev/null
    git clean -dffx
    git reset --hard HEAD
    git pull
}

function requirement_update {
    echo "检测到requirement.txt有变化，重新安装依赖..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirement.txt
}

function package_list_update {
    echo "检测到package_list.txt有变化，更新软件包..."
    apk add --no-cache $(echo $(cat docker/package_list.txt))
}

if [ "${EmbyTools_AUTO_UPDATE}" = "true" ]; then
    if [ ! -s /tmp/requirement.txt.sha256sum ]; then
        sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
    fi
    if [ ! -s /tmp/package_list.txt.sha256sum ]; then
        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
    fi
    app_update
    if [ $? -eq 0 ]; then
        echo "更新成功..."
        hash_old=$(cat /tmp/requirement.txt.sha256sum)
        hash_new=$(sha256sum requirement.txt)
        if [ "$hash_old" != "$hash_new" ]; then
            requirement_update
            if [ $? -ne 0 ]; then
                echo "无法安装依赖，请更新镜像..."
            else
                echo "依赖安装成功..."
                sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
                hash_old=$(cat /tmp/package_list.txt.sha256sum)
                hash_new=$(sha256sum docker/package_list.txt)
                if [ "$hash_old" != "$hash_new" ]; then
                    package_list_update
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

if [[ "$(stat -c '%u' ${EMBYTOOLS_CONFIG})" != "${PUID}" ]] || [[ "$(stat -c '%g' ${EMBYTOOLS_CONFIG})" != "${PGID}" ]]; then
    chown ${PUID}:${PGID} ${EMBYTOOLS_CONFIG}
fi

if [[ "$(stat -c '%A' ${WORK_DIR}/docker/start.sh)" != "-rwxr-xr-x" ]]; then
chmod 755 ${WORK_DIR}/docker/start.sh
fi

umask ${UMASK}

# 启动
echo -e "——————————————————————————————————————————————————————————"
cat ${WORK_DIR}/docker/EmbyTools
echo -e "

以PUID=${PUID}，PGID=${PGID}，Umask=${UMASK}的身份启动程序
—————————————————————————————————————————————————————————— 

"

exec su-exec ${PUID}:${PGID} python3 main.py
