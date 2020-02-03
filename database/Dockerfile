ARG BASE_IMAGE=mariadb

FROM $BASE_IMAGE

ARG SHINOBI_REPOSITORY_URL=https://gitlab.com/Shinobi-Systems/Shinobi.git
ARG SHINOBI_REPOSITORY_BRANCH=master

RUN apt-get update \
	&& apt-get install --no-install-recommends -y \
		ca-certificates \
		git \
	&& tempDirectory="$(mktemp -d)" \
	&& git clone --depth=1 --branch="${SHINOBI_REPOSITORY_BRANCH}" "${SHINOBI_REPOSITORY_URL}" "${tempDirectory}" \
	&& mv "${tempDirectory}/sql/framework.sql" /docker-entrypoint-initdb.d \
	&& rm -r "${tempDirectory}" \
	&& apt-get purge -y \
		git \
		ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

ADD server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf

