#!/usr/bin/env bash

set -euf -o pipefail

"${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-config.py"
"${DOCKER_SHINOBI_INSTALL_DIRECTORY}/generate-super-config.sh"

export MYSQL_PWD="${MYSQL_ROOT_PASSWORD}"
host="$(jq -r '.db.host' /opt/shinobi/conf.json)"
port="$(jq -r '.db.port' /opt/shinobi/conf.json)"

# XXX: Could use knex (library Shinobi uses) to do this
>&2 echo "Waiting for database to be ready..."
while ! mysqladmin ping --host="${host}" --port="${port}" --user=root --silent; do
	sleep 0.5
done
>&2 echo "Database is ready!"
 
cd "${SHINOBI_INSTALL_DIRECTORY}"
node camera.js
