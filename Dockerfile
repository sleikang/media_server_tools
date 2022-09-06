FROM alpine:3.16

ENV TZ=Asia/Shanghai

COPY --chmod=755 . /opt

RUN apk add --update --no-cache \
    python3-dev \
    py3-pip \
    bash \
    tzdata && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install pyyaml && \
    pip install html2text && \
    cp /opt/config/config.yaml /home/config.yaml
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

CMD [ "/opt/start.sh" ]
