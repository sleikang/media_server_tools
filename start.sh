#!/bin/bash

function setting {

touch /setting.lock

mkdir -p /opt/logs
touch /opt/logs/EmbyChineseNameSynchronous.log

ln -sf /usr/share/zoneinfo/$TZ   /etc/localtime
echo $TZ > /etc/timezone

cat > /opt/main.py <<EOF
import time
from embyserver import embyserver

#EMBY 域名 包含http(s)和端口号后面不带/
#例如https://xxx.xxx.xxx:8920
embyhost = '$EMBYHOST'
#EMBY 用户ID 进EMBY 用户点击管理员账号配置可以在网址上看到userId
embyuserid = '$EMBYUSERID'
#EMBY APIKEY
embykey = '$EMBYKEY'
#TMDB APIKEY
tmdbkey = '$TMDBKEY'
#线程数量
threadnum = $THREADNUM
#是否刷新人名
updatepeople = $UPDATEPEOPLE
#每次刷新全部媒体间隔时间 [小时]
updatetime = $UPDATETIME

if __name__ == '__main__':
    embymediaclient = embyserver(embyhost=embyhost, embyuserid=embyuserid, embykey=embykey, tmdbkey=tmdbkey, threadnum=threadnum, updatepeople=updatepeople)
    while True:
        try:
            print('开始刷新媒体库元数据')
            embymediaclient.update_media_name()
            print('刷新媒体库元数据完成')
        except Exception as reuslt:
            print(reuslt)

EOF

}

if [ ! -f /setting.lock ]; then
	setting
fi

cd /opt
python3 main.py >> /opt/logs/EmbyChineseNameSynchronous.log