ARG BASE_IMAGE_WITH_FFMPEG=colinnolan/ffmpeg:latest

FROM ${BASE_IMAGE_WITH_FFMPEG}

ENV SHINOBI_INSTALL_DIRECTORY=/opt/shinobi
ENV DOCKER_SHINOBI_INSTALL_DIRECTORY=/opt/docker-shinobi

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
		git \
		jq \
		mariadb-client \
		procps \
	&& rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_11.x | bash - \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		nodejs \
	&& rm -rf /var/lib/apt/lists/*

ARG SHINOBI_REPOSITORY_URL=https://gitlab.com/Shinobi-Systems/Shinobi.git
ARG SHINOBI_REPOSITORY_BRANCH=master
RUN git clone --depth=1 --branch="${SHINOBI_REPOSITORY_BRANCH}" "${SHINOBI_REPOSITORY_URL}" "${SHINOBI_INSTALL_DIRECTORY}" \
	&& cd "${SHINOBI_INSTALL_DIRECTORY}" \
	&& npm install

COPY generate-config.py "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/"
COPY generate-super-config.sh "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/"
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh \
    "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-config.py" \
    "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-super-config.sh"

CMD ["/docker-entrypoint.sh"]
 
