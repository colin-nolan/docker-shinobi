#!/usr/bin/python3

import os
import json

CONFIG_SOURCE = "/etc/shinobi/conf.json"
CONFIG_DESTINATION = "/opt/shinobi/conf.json"

MYSQL_HOST = "MYSQL_HOST"
MYSQL_USER = "MYSQL_USER"
MYSQL_PASSWORD = "MYSQL_PASSWORD"
MYSQL_DATABASE = "MYSQL_DATABASE"

if os.path.exists(CONFIG_DESTINATION):
    raise RuntimeError(f"Cannot generate configuration file as one is already in place: {CONFIG_DESTINATION}")

with open(CONFIG_SOURCE, "r") as file:
    configuration = json.load(file)

if "db" not in configuration:
    configuration["db"] = {
        "host": os.environ[MYSQL_HOST_PARAMETER],    
        "port": os.environ[MYSQL_PORT_PARAMETER],
        "user": os.environ[MYSQL_USER_PARAMETER],
        "password": os.environ[MYSQL_DATABASE_PARAMETER]
    }

with open(CONFIG_DESTINATION, "w") as file:
    file.write(CONFIG_DESTINATION)


