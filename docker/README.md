# EmbyTools

Emby 媒体标题自动同步
1. 中文标题
2. 媒体概述
3. 中文人名
4. 中文扮演
5. 剧集概述评分图片同步
6. 剧集组自定义同步
7. 媒体搜刮检查是否正确(配合NasTools)


*  注意使用本工具需要emby本身刮削了tmdb的完整数据，工具只是获取原有的数据进行替换
*  设置了`EmbyTools_AUTO_UPDATE`=true，重启容器即可自动更新EmbyTools程序

**docker-cli**

```
docker run -itd \
  --name EmbyTools \
  -v /root/config:/config \
  -e TZ=Asia/Shanghai \
  -e PUID=1000 \
  -e PGID=1000 \
  -e UMASK=022 \
  -e ECNS_AUTO_UPDATE=true \
  --net=host \
  ddsderek/embytools:latest
```

**docker-compose**

```
version: '3.3'
services:
    embytools:
        container_name: EmbyTools
        volumes:
            - './config:/config'
        environment:
            - TZ=Asia/Shanghai
            - PUID=1000
            - PGID=1000
            - UMASK=022
            - ECNS_AUTO_UPDATE=true # 自动更新
        network_mode: host
        image: 'ddsderek/embytools:latest'
```
