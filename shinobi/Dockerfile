FROM node:11-stretch

ENV SHINOBI_INSTALL_DIRECTORY=/opt/shinobi
ENV DOCKER_SHINOBI_INSTALL_DIRECTORY=/opt/docker-shinobi

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		curl \
		jq \
	&& apt-get install -y \
		ffmpeg \
	&& rm -rf /var/lib/apt/lists/*

ARG SHINOBI_REPOSITORY_URL=https://gitlab.com/Shinobi-Systems/Shinobi.git
ARG SHINOBI_REPOSITORY_BRANCH=master

RUN git clone --depth=1 --branch="${SHINOBI_REPOSITORY_BRANCH}" "${SHINOBI_REPOSITORY_URL}" "${SHINOBI_INSTALL_DIRECTORY}" \
	&& cd "${SHINOBI_INSTALL_DIRECTORY}" \
	&& npm install
RUN npm install ffbinaries

# TODO: Move up
RUN apt-get update && apt-get install -y mariadb-client

ADD generate-config.py "${DOCKER_SHINOBI_INSTALL_DIRECTORY}/"
ADD docker-entrypoint.sh /

CMD ["/docker-entrypoint.sh"]
 