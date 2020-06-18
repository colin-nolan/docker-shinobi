ARG BASE_IMAGE=mariadb

FROM alpine as shinobi-downloader

ARG SHINOBI_REPOSITORY_URL=https://gitlab.com/Shinobi-Systems/Shinobi.git
ARG SHINOBI_REPOSITORY_BRANCH=master
ARG SHINOBI_REPOSITORY_COMMIT

RUN apk add \
		ca-certificates \
		git

RUN git clone --branch="${SHINOBI_REPOSITORY_BRANCH}" "${SHINOBI_REPOSITORY_URL}" /usr/local/src/shinobi
WORKDIR /usr/local/src/shinobi
RUN if [ "${SHINOBI_REPOSITORY_COMMIT}" != "" ]; then \
        git log -1; \
        git checkout "${SHINOBI_REPOSITORY_COMMIT}"; \
    fi


FROM $BASE_IMAGE

COPY --from=shinobi-downloader /usr/local/src/shinobi/sql/framework.sql /docker-entrypoint-initdb.d

ADD server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf

