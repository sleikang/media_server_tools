FROM alpine:3.16

ENV EMBYHOST=embyhost \
    EMBYUSERID=embyuserid \
    EMBYKEY=embykey \
    TMDBKEY=tmdbkey \
    THREADNUM=16 \
    UPDATEPEOPLE=True \
    UPDATEOVERVIEW=True \
    UPDATETIME=1 \
    TZ=Asia/Shanghai

RUN apk add --update --no-cache \
    python3-dev \
    py3-pip \
    bash \
    tzdata && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install yaml && \
    pip install logging && \
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

COPY --chmod=755 . /opt

CMD [ "/opt/start.sh" ]
