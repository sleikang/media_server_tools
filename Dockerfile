FROM frolvlad/alpine-python3

ENV TZ=Asia/Shanghai

RUN apk add --update --no-cache \
    bash \
    tzdata && \
    pip install zhconv && \
    pip install requests && \
    pip install simplejson && \
    pip install pyyaml && \
    pip install logging && \
    # 清理
    rm -rf /tmp/* /root/.cache /var/cache/apk/*

COPY --chmod=755 . /opt

CMD [ "/opt/start.sh" ]
