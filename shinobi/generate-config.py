#!/usr/bin/python3

import os
import json
import sys

CONFIG_SOURCE = "/mnt/host/conf.json"

MYSQL_HOST_PARAMETER = "MYSQL_HOST"
MYSQL_PORT_PARAMETER = "MYSQL_PORT"
MYSQL_USER_PARAMETER = "MYSQL_USER"
MYSQL_PASSWORD_PARAMETER = "MYSQL_PASSWORD"
MYSQL_DATABASE_PARAMETER = "MYSQL_DATABASE"

config_destination = os.path.join(os.environ["SHINOBI_INSTALL_DIRECTORY"], "conf.json")

with open(CONFIG_SOURCE, "r") as file:
    configuration = json.load(file)

if "db" not in configuration:
    configuration["db"] = {
        "host": os.environ[MYSQL_HOST_PARAMETER],    
        "port": os.environ[MYSQL_PORT_PARAMETER],
        "user": os.environ[MYSQL_USER_PARAMETER],
        "password": os.environ[MYSQL_PASSWORD_PARAMETER],
        "database": os.environ[MYSQL_DATABASE_PARAMETER]
    }

with open(config_destination, "w") as file:
    json.dump(configuration, file, sort_keys=True, indent=4)

print("Generated Shinobi configuration: %s" % (config_destination, ), file=sys.stderr)
