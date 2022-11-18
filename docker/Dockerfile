FROM alpine:3.16

ENV WORK_DIR=/ecns \
    LANG="C.UTF-8" \
    PS1="\u@\h:\w \$ " \
    TZ=Asia/Shanghai \
    PUID=1000 \
    PGID=1000 \
    UMASK=022

RUN \
    # 软件包安装
    apk add --no-cache \
        $(echo $(wget --no-check-certificate -qO- https://raw.githubusercontent.com/DDS-Derek/EmbyChineseNameSynchronous/main/docker/package_list.txt)) \
    && \
    # Python库安装
    pip install -r \
        https://raw.githubusercontent.com/DDS-Derek/EmbyChineseNameSynchronous/main/requirement.txt \
    && \
    git clone https://github.com/DDS-Derek/EmbyChineseNameSynchronous.git ${WORK_DIR} && \
    chmod -R 755 ${WORK_DIR} && \
    rm -rf \
        /tmp/* \
        /root/.cache \
        /var/cache/apk/*

CMD [ "/ecns/docker/start.sh" ]
