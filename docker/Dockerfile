FROM alpine:3.16

ENV EMBYHOST=embyhost \
    EMBYUSERID=embyuserid \
    EMBYKEY=embykey \
    TMDBKEY=tmdbkey \
    THREADNUM=16 \
    UPDATEPEOPLE=True\
    UPDATETIME=1

RUN apk add --update --no-cache \
    python3-dev \
    py3-pip \
    git \
    bash \
    tzdata && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    # 下载源码
    git clone https://github.com/sleikang/EmbyChineseNameSynchronous.git /opt && \
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

COPY --chmod=755 ./start.sh /start.sh

CMD [ "/start.sh" ]