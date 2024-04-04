# media_server_tools

Emby/Jellyfin/Plex 媒体中文自动同步

1. 中文标题
2. 媒体概述
3. 中文人名(Plex 暂时不支持)
4. 中文扮演(Plex 暂时不支持)
5. 剧集概述评分图片同步
6. 剧集组自定义同步
7. 媒体搜刮检查是否正确(配合 NasTools)

-   注意使用本工具需要媒体服务器本身刮削了 tmdb 的完整数据，工具只是获取原有的数据进行替换使用方式
-   源码运行

1. 配置文件 config/config.yaml
2. win 下使用安装 Python3 安装过程连续点击下一步
3. 安装依赖模块

-   python -m pip install -r requirement.txt

4. 启动 cmd 输入 python main.py

-   exe 运行

1. 下载发布版本
2. 配置文件 config/config.yaml
3. 启动 media_server_tools.exe

-   docker compose 运行

```
version: '3'

services:
  jd_server:
    image: sleikang/media_server_tools:latest
    container_name: media_server_tools
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - /your_path/media_server_tools/log:/app/log #日志文件目录
      - /your_path/media_server_tools/config:/app/config #配置文件目录
    restart: always

```

-   docker run

```
docker run -d \
  --name media_server_tools \
  -e TZ=Asia/Shanghai \
  -v /your_path/media_server_tools/log:/app/log \
  -v /your_path/media_server_tools/config:/app/config \
  --restart always \
  sleikang/media_server_tools:latest

```

![image](https://user-images.githubusercontent.com/23020770/188265314-73610b4e-264d-4b8c-9750-e707512f7fef.png) ![image](https://user-images.githubusercontent.com/23020770/188306989-c722673e-2dac-4c79-8cb1-1a4eb3a35aa2.png) ![image](https://user-images.githubusercontent.com/23020770/202453243-255b1c95-cbdf-4f24-a215-16399a442ff6.png)
