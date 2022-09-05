FROM alpine:3.16

ENV TZ=Asia/Shanghai

RUN apk add --update --no-cache \
    python3-dev \
    py3-pip \
    bash \
    tzdata && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install pyyaml && \
    python3 -m pip install --upgrade setupTools && \
    python3 -m pip install --upgrade pip && \
    pip install logging && \
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

COPY --chmod=755 . /opt

CMD [ "/opt/start.sh" ]
