FROM alpine:3.16

ENV TZ=Asia/Shanghai \
    PUID=1000 \
    PGID=1000

RUN apk add --update --no-cache \
    python3-dev \
    py3-pip \
    bash \
    git \
    tzdata \
    supervisor && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install pyyaml && \
    pip install html2text && \
    git clone https://github.com/sleikang/EmbyChineseNameSynchronous.git /opt && \
    chmod -R 755 /opt && \
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

CMD [ "/opt/docker/start.sh" ]
