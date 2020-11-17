# Deploy BlueBanquise inside a single Podman container

## Prepare host

dnf install podman

setsebool -P container_manage_cgroup true

Ensure latest centos 8 dvd iso is copied in /var/www/html/repositories/centos/8/x86_64/os/

## Build image

podman pull centos:latest
podman build --tag centos:bb -f ./Dockerfile

## Start container

podman run -d --net=host --no-hosts=true --hostname=management1 -v /var/www/html/repositories/centos/8/x86_64/os/:/var/www/html/repositories/centos/8/x86_64/os/:Z --name bbtest centos:bbtest
podman exec -it bbtest /bin/bash

