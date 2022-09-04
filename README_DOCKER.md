**docker-cli**

```
docker run -itd \
  --name EmbyChineseNameSynchronous \
  -v ./logs:/opt/logs \
  -e EMBYHOST=embyhost \
  -e EMBYUSERID=embyuserid \
  -e EMBYKEY=embykey \
  -e TMDBKEY=tmdbkey \
  -e THREADNUM=16 \
  -e UPDATEPEOPLE=True \
  -e UPDATEOVERVIEW=True \
  -e UPDATETIME=1 \
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
            - './logs:/opt/logs'
        environment:
            - EMBYHOST=embyhost
            - EMBYUSERID=embyuserid
            - EMBYKEY=embykey
            - TMDBKEY=tmdbkey
            - THREADNUM=16
            - UPDATEPEOPLE=True
            - UPDATEOVERVIEW=True
            - UPDATETIME=1
            - TZ=Asia/Shanghai
        image: 'ddsderek/embychinesenamesynchronous:latest'
```
