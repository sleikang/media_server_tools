FROM alpine:3.16

ENV TZ=Asia/Shanghai

RUN apk add --update --no-cache \
    gcc \
    python3-dev \
    python3 \
    py3-pip \
    bash \
    tzdata && \
    pip install --upgrade pip setuptools wheel && \
    pip install pip==20.3.3 && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install pyyaml && \
    pip install logging && \
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

COPY --chmod=755 . /opt

CMD [ "/opt/start.sh" ]
