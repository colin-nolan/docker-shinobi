[![Build Status](https://travis-ci.com/colin-nolan/docker-shinobi.svg?branch=master)](https://travis-ci.com/colin-nolan/docker-shinobi)
# Dockerised Shinobi
_Dockerised installation of [Shinobi](https://gitlab.com/Shinobi-Systems/Shinobi) (an open-source video management 
solution)._


## Requirements
- Docker and Docker Compose.
- Works on Raspberry Pi (with some configuration changes).


## Setup
*For an Ansible installation (including user and monitor setup), 
[please see `colin_nolan.shinobi`](https://github.com/colin-nolan/ansible-shinobi/)*.

### Trying it Out
The instructions below should get a Dockerised Shinobi installation going with minimal effort.

_This setup should _not_ be used in production!_ 
See [below for production setup suggestions](#Production).

```bash
env \
        SHINOBI_SUPER_USER_EMAIL=example@localhost \
        SHINOBI_SUPER_USER_PASSWORD=password123 \
        SHINOBI_SUPER_USER_TOKEN=token123 \
        MYSQL_ROOT_PASSWORD=password123 \
        MYSQL_USER_PASSWORD=password123 \
        SHINOBI_VIDEO_LOCATION="${PWD}/shinobi-data/videos" \
        SHINOBI_DATA_LOCATION="${PWD}/shinobi-data/database" \
    docker-compose up
```
_Note: on a Mac, the above will result in error 
[due to an issue bind mounting time related files from /etc](https://github.com/docker/for-mac/issues/2396). 
To quickly get around this, set the environment variables: `SHINOBI_LOCALTIME=/dev/null SHINOBI_TIMEZONE=/dev/null`._

Once the installation is going, [jump into the super user interface (using the credentials defined above) and create a 
user: http://localhost:8080/super](http://localhost:8080/super).

You will then be able to [login on the home page](http://localhost:8080) to setup CCTV monitors. 


## Production
_The advice below is given as suggestions only - I take no responsibility for how you setup your software!_
- I would not recommend exposing any of Shinobi's interfaces to untrusted parties. 
- Don't set passwords to `password123`...
- You may be able to build a more optimised version of [ffmpeg](https://www.ffmpeg.org/) for your machine than the one 
  provided. A custom (Debian-based) base Docker image with `ffmpeg` on the path can be used by setting 
  the environment variable `BASE_IMAGE_WITH_FFMPEG`.


## Raspberry Pi
The setup will work on a Raspberry Pi with a few configuration adjustments.
- MariaDB does not have armfh installation - use `DATABASE_BASE_IMAGE=jsurf/rpi-mariadb`.
- Change Shinobi base image (with `ffmpeg`) to be an image compatible for your RPi's architecture, using 
  `SHINOBI_BASE_IMAGE`. A [pre-made setup for such an image is available on GitHub](https://github.com/colin-nolan/docker-ffmpeg-rpi).


## Related
- [Ansible Shinobi setup](https://github.com/colin-nolan/ansible-shinobi).
- [Shinobi Python client](https://github.com/colin-nolan/python-shinobi).


## Legal
[AGPL v3.0](LICENSE). Copyright 2019, 2020, 2021 Colin Nolan.

I am not affiliated to the development of Shinobi project in any way. 

This work is in no way related to the company that I work for.
