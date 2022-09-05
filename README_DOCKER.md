**docker-cli**

```
docker run -itd \
  --name EmbyChineseNameSynchronous \
  -v ./config:/opt/config \
  -e TZ=Asia/Shanghai \
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
        image: 'ddsderek/embychinesenamesynchronous:latest'
```
