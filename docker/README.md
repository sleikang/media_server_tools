**docker-cli**

```
docker run -itd \
  --name EmbyChineseNameSynchronous \
  -v ./config:/opt/config \
  -e TZ=Asia/Shanghai \
  -e PUID=1000 \
  -e PGID=1000 \
  -e UMASK=022 \
  --net=host \
  ddsderek/embychinesenamesynchronous:latest
```

**docker-compose**

```
version: '3.3'
services:
    embychinesenamesynchronous:
        container_name: EmbyChineseNameSynchronous
        volumes:
            - './config:/opt/config'
        environment:
            - TZ=Asia/Shanghai
            - PUID=1000
            - PGID=1000
            - UMASK=022
        network_mode: host
        image: 'ddsderek/embychinesenamesynchronous:latest'
```
