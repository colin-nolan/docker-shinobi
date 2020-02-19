#!/usr/bin/env bash

set -euf -o pipefail

configDestination="${SHINOBI_INSTALL_DIRECTORY}/super.json"

jq -n "[.mail=\"${SHINOBI_SUPER_USER_EMAIL}\" | .pass=\"${SHINOBI_SUPER_USER_PASSWORD}\" | .tokens=[\"${SHINOBI_SUPER_USER_TOKEN}\"]]" \
    > "${configDestination}"

>&2 echo "Generated Shinobi super configuration: ${configDestination}"
