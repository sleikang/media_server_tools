FROM alpine:3.16

ENV WORK_DIR=/MediaServerTools \
    EMBYTOOLS_CONFIG=/config \
    LANG="C.UTF-8" \
    PS1="\u@\h:\w \$ " \
    TZ=Asia/Shanghai \
    PUID=1000 \
    PGID=1000 \
    UMASK=022 \
    REPO_URL=https://github.com/DDS-Derek/MediaServerTools.git \
    REPO_RAW_URL=https://raw.githubusercontent.com/DDS-Derek/MediaServerTools \
    MediaServerTools_AUTO_UPDATE=true

WORKDIR ${WORK_DIR}

RUN \
    # 软件包安装
    apk add --no-cache \
        $(echo $(wget --no-check-certificate -qO- ${REPO_RAW_URL}/main/docker/package_list.txt)) \
    && \
    # Python库安装
    pip install --upgrade pip setuptools wheel \
    && \
    pip install -r \
        ${REPO_RAW_URL}/main/requirement.txt \
    && \
    rm -rf \
        /tmp/* \
        /root/.cache \
        /var/cache/apk/*

RUN git config --global pull.ff only && \
    git clone -b main ${REPO_URL} ${WORK_DIR} --recurse-submodule && \
    git config --global --add safe.directory ${WORK_DIR} && \
    chmod -R 755 ${WORK_DIR}

ENTRYPOINT [ "/MediaServerTools/docker/start.sh" ]
