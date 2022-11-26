# MediaServerTools

## 简介

Emby/Jellyfin/Plex 媒体中文自动同步
1. 中文标题
2. 媒体概述
3. 中文人名(Plex暂时不支持)
4. 中文扮演(Plex暂时不支持)
5. 剧集概述评分图片同步
6. 剧集组自定义同步
7. 媒体搜刮检查是否正确(配合NasTools)

- Dockerhub: https://hub.docker.com/r/ddsderek/mediaservertools
- Github: https://github.com/sleikang/MediaServerTools

*  注意使用本工具需要媒体服务器本身刮削了tmdb的完整数据，工具只是获取原有的数据进行替换

## 部署

设置`MediaServerTools_AUTO_UPDATE`=true，重启容器即可自动更新MediaServerTools程序

**docker-cli**

```
docker run -itd \
  --name MediaServerTools \
  -v /root/config:/config \
  -e TZ=Asia/Shanghai \
  -e PUID=1000 \
  -e PGID=1000 \
  -e UMASK=022 \
  -e MediaServerTools_AUTO_UPDATE=true \
  --net=host \
  ddsderek/mediaservertools:latest
```

**docker-compose**

```
version: '3.3'
services:
    MediaServerTools:
        container_name: MediaServerTools
        volumes:
            - './config:/config'
        environment:
            - TZ=Asia/Shanghai
            - PUID=1000
            - PGID=1000
            - UMASK=022
            - MediaServerTools_AUTO_UPDATE=true # 自动更新
        network_mode: host
        image: 'ddsderek/mediaservertools:latest'
```


![image](https://user-images.githubusercontent.com/23020770/188265314-73610b4e-264d-4b8c-9750-e707512f7fef.png)
![image](https://user-images.githubusercontent.com/23020770/188306989-c722673e-2dac-4c79-8cb1-1a4eb3a35aa2.png)
![image](https://user-images.githubusercontent.com/23020770/202453243-255b1c95-cbdf-4f24-a215-16399a442ff6.png)
