#!/usr/bin/env bash

set -euf -o pipefail

temp_directory=$(mktemp -d -t "shinobi-data.XXXXXXXXX")
if [[ "${temp_directory}" =~ ^/var ]]; then
    # Mac creates temp directories in /var, which then can't be mounted...
    mv "${temp_directory}" /tmp
    temp_directory="/tmp/$(basename "${temp_directory}")"
fi
trap 'rm -rf "${temp_directory}"' EXIT

env \
      SHINOBI_SUPER_USER_EMAIL=example@localhost \
      SHINOBI_SUPER_USER_PASSWORD=password123 \
      SHINOBI_SUPER_USER_TOKEN=token123 \
      MYSQL_ROOT_PASSWORD=password123 \
      MYSQL_USER_PASSWORD=password123 \
      SHINOBI_VIDEO_LOCATION="${temp_directory}/shinobi-data/videos" \
      SHINOBI_DATA_LOCATION="${temp_directory}/shinobi-data/database" \
      SHINOBI_LOCALTIME=/dev/null SHINOBI_TIMEZONE=/dev/null \
    docker-compose up &

wait-for-it \
        --service 0.0.0.0:8080 \
        --timeout 0 \
    -- echo "Shinobi web interface is running"

docker-compose down