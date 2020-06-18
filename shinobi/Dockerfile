ARG BASE_IMAGE_WITH_FFMPEG=colinnolan/ffmpeg:latest

FROM ${BASE_IMAGE_WITH_FFMPEG}

ENV SHINOBI_INSTALL_DIRECTORY=/opt/shinobi
ENV DOCKER_SHINOBI_INSTALL_DIRECTORY=/opt/docker-shinobi

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        jq \
        mariadb-client \
        procps \
        python  \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        nodejs \
    && rm -rf /var/lib/apt/lists/*

ARG SHINOBI_REPOSITORY_URL=https://gitlab.com/Shinobi-Systems/Shinobi.git
ARG SHINOBI_REPOSITORY_BRANCH=master
ARG SHINOBI_REPOSITORY_COMMIT
RUN git clone --branch="${SHINOBI_REPOSITORY_BRANCH}" "${SHINOBI_REPOSITORY_URL}" "${SHINOBI_INSTALL_DIRECTORY}" \
    && cd "${SHINOBI_INSTALL_DIRECTORY}" \
    && if [ "${SHINOBI_REPOSITORY_COMMIT}" != "" ]; then \
           git checkout "${SHINOBI_REPOSITORY_COMMIT}"; \
       fi \
    && npm install

COPY generate-config.py "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/"
COPY generate-super-config.sh "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/"
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x \
    /docker-entrypoint.sh \
    "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-config.py" \
    "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-super-config.sh"

ENTRYPOINT ["/docker-entrypoint.sh"]
 
HEALTHCHECK --interval=10m --start-period=30s \
    CMD curl -f http://localhost:8080 || exit 1

