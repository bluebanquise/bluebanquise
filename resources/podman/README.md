# Deploy BlueBanquise inside a single Podman container

## Prepare host

Install podman:

.. code-block:: text

  dnf install podman

Enable systemd inside containers:

.. code-block:: text

  setsebool -P container_manage_cgroup true

And ensure latest centos 8 dvd iso is copied in */var/www/html/repositories/centos/8/x86_64/os/* .

## Build image

Grab latest centos:

.. code-block:: text

  podman pull centos:latest

And build BlueBanquise base image for management node:

.. code-block:: text

  podman build --tag centos:bb -f ./Dockerfile

## Start container

Now, start the container using the following command:

.. code-block:: text

  podman run -d --net=host --no-hosts=true --hostname=management1 -v /var/www/html/repositories/centos/8/x86_64/os/:/var/www/html/repositories/centos/8/x86_64/os/:Z --name bbtest centos:bbtest
  
Few details:

* --net=host will allow access of the entire network of the main host to the container.
* -no-hosts=true will prevent auto generation of /etc/hosts inside the container.
* -v /var/www/html/repositories/centos/8/x86_64/os/:/var/www/html/repositories/centos/8/x86_64/os/:Z will map your current Centos 8 iso copy into the container.

Ensure container is running, using:

.. code-block:: text

  podman ps -a

Note that vou can start or stop the container using:

.. code-block:: text

  podman stop bbtest
  podman start bbtest

Once container is started, you can attach to it using:

.. code-block:: text

  podman exec -it bbtest /bin/bash

By default, ssh server of the container listen on port 2222, to avoid conflict with main host.

If you wish to start services inside the container (http, dns, dhcp, etc), ensure first to stop them if exist on the main host, to avoid ports conflicts.
