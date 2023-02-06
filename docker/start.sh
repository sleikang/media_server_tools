#!/bin/bash

Green="\033[32m"
Red="\033[31m"
Yellow='\033[33m'
Font="\033[0m"
INFO="[${Green}INFO${Font}]"
ERROR="[${Red}ERROR${Font}]"
WARN="[${Yellow}WARN${Font}]"
Time=$(date +"%Y-%m-%d %T")
INFO(){
echo -e "${Time} ${INFO} ${1}"
}
ERROR(){
echo -e "${Time} ${ERROR} ${1}"
}
WARN(){
echo -e "${Time} ${WARN} ${1}"
}

# 初始设置
function setting {
    touch /setting.lock

    # 兼容旧config文件路径
    if [ -d /opt/config ] && [ ! -d /config ]; then
        INFO "使用v1.x版本config路径配置"
        rm -rf /config
        ln -s /opt/config /
    else
        mkdir -p /config
    fi
}

# 自动更新
function app_update {
    INFO "更新程序..."
    git remote set-url origin ${REPO_URL} &>/dev/null
    git clean -dffx
    git reset --hard HEAD
    git pull
}

function requirement_update {
    INFO "检测到requirement.txt有变化，重新安装依赖..."
    if [ "${MediaServerTools_CN_UPDATE}" = "true" ]; then
        pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    else
        pip install --upgrade pip setuptools wheel
        pip install -r requirement.txt
    fi
}

function package_list_update {
    INFO "检测到package_list.txt有变化，更新软件包..."
    if [ "${NASTOOL_CN_UPDATE}" = "true" ]; then
        sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
        apk update -f
    fi
    apk add --no-cache $(echo $(cat docker/package_list.txt))
}

function backup_config {
    INFO "备份config文件中..."
    if [ -f /config/config_backup.zip ]; then
        rm -rf /config/config_backup.zip
    fi
    if [ -f /config/log.txt ]; then
        zip -r /config/config_backup.zip /config -x='/config/log.txt'
    else
        zip -r /config/config_backup.zip /config
    fi
    if [ -f /config/config_backup.zip ]; then
        if [[ "$(stat -c '%u' /config/config_backup.zip)" != "${PUID}" ]] || [[ "$(stat -c '%g' /config/config_backup.zip)" != "${PGID}" ]]; then
            chown ${PUID}:${PGID} /config/config_backup.zip
        fi
        if [ $? -ne 0 ]; then
            ERROR "备份失败，未成功设置权限"
        else
            INFO "备份成功"
        fi
    else
        ERROR "备份失败,未正常生成文件"
    fi
}

if [ ! -f /setting.lock ]; then
	setting
fi

if [ "${MediaServerTools_AUTO_UPDATE}" = "true" ]; then
    backup_config
    if [ ! -s /tmp/requirement.txt.sha256sum ]; then
        sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
    fi
    if [ ! -s /tmp/package_list.txt.sha256sum ]; then
        sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
    fi
    app_update
    if [ $? -eq 0 ]; then
        INFO "更新成功..."
        hash_old=$(cat /tmp/requirement.txt.sha256sum)
        hash_new=$(sha256sum requirement.txt)
        if [ "$hash_old" != "$hash_new" ]; then
            requirement_update
            if [ $? -ne 0 ]; then
                ERROR "无法安装依赖，请更新镜像"
            else
                INFO "依赖安装成功"
                sha256sum requirement.txt > /tmp/requirement.txt.sha256sum
            fi
        fi
        hash_old=$(cat /tmp/package_list.txt.sha256sum)
        hash_new=$(sha256sum docker/package_list.txt)
        if [ "$hash_old" != "$hash_new" ]; then
            package_list_update
            if [ $? -ne 0 ]; then
                ERROR "无法更新软件包，请更新镜像"
            else
                INFO "软件包安装成功"
                sha256sum docker/package_list.txt > /tmp/package_list.txt.sha256sum
            fi
        fi
    else
        WARN "更新失败，继续使用旧的程序来启动"
    fi
else
    INFO "程序自动升级已关闭，如需自动升级请在创建容器时设置环境变量：MediaServerTools_AUTO_UPDATE=true"
fi

# 权限设置
chown -R ${PUID}:${PGID} ${WORK_DIR}

# 兼容旧环境变量
if [[ -n "${MEDIASERVERTOOLS_CONFIG}" ]]; then
    if [[ "$(stat -c '%u' ${MEDIASERVERTOOLS_CONFIG})" != "${PUID}" ]] || [[ "$(stat -c '%g' ${MEDIASERVERTOOLS_CONFIG})" != "${PGID}" ]]; then
        chown ${PUID}:${PGID} ${MEDIASERVERTOOLS_CONFIG}
    fi
fi
if [[ -n "${EMBYTOOLS_CONFIG}" ]]; then
    WARN "使用旧Config路径环境变量"
    if [[ "$(stat -c '%u' ${EMBYTOOLS_CONFIG})" != "${PUID}" ]] || [[ "$(stat -c '%g' ${EMBYTOOLS_CONFIG})" != "${PGID}" ]]; then
        chown ${PUID}:${PGID} ${EMBYTOOLS_CONFIG}
    fi
fi

if [[ "$(stat -c '%A' ${WORK_DIR}/docker/start.sh)" != "-rwxr-xr-x" ]]; then
chmod 755 ${WORK_DIR}/docker/start.sh
fi

umask ${UMASK}

# 启动
echo -e "————————————————————————————————————————————————————————————————————————————————————————"
cat ${WORK_DIR}/docker/MediaServerTools
echo -e "

以PUID=${PUID}，PGID=${PGID}，Umask=${UMASK}的身份启动程序
———————————————————————————————————————————————————————————————————————————————————————— 

"

exec su-exec ${PUID}:${PGID} python3 main.py
