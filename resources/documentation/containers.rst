==========
Containers
==========

There are many ways to put BlueBanquise stack inside containers.
The stack was designed to be able to spread services over multiple management
nodes, and so also run in containers or VMs.

A very simple way is described here, but not designed for production. However,
this can be used as a starting point.

Podman was chosen as containers tool, as it allows simple systemd usage inside
containers without needed additional tuning or unsecure privileged containers.

Podman
======

Install podman and grab base image
----------------------------------

Install podman

.. code-block:: text

  dnf config-manager --set-enabled PowerTools
  dnf install -y @container-tools

Enable systemd in Podman

.. code-block:: text

  setsebool -P container_manage_cgroup true

Grab latest centos image:

.. code-block:: text

  podman pull centos:latest

Generic ansible ready image
---------------------------

Create a generic image, that contains python3 only (centos **W**ith
**P**ython**3**).

First create centoswp3 dir:

.. code-block:: text

  mkdir /root/centoswp3
  cd /root/centoswp3

Create file Dockerfile with the following content:

.. code-block:: text

  FROM centos

  RUN dnf -y install python3; dnf clean all;

  CMD [ "/sbin/init" ]

And build the new image, and name it centoswp3:

.. code-block:: text

  podman build --tag centos:centoswp3 -f ./Dockerfile

Once done, check your new source image is ready:

.. code-block:: bash

  [root@pc-200 centoswp3]# podman images
  REPOSITORY                 TAG         IMAGE ID       CREATED         SIZE
  localhost/centos           centoswp3   aa79704b7475   4 seconds ago   245 MB
  docker.io/library/centos   latest      831691599b88   3 weeks ago     223 MB
  [root@pc-200 centoswp3]#

Example: repositories container
-------------------------------

Now start a container, called repositories. There are two ways:

Unsecure but simpler:

.. code-block:: bash

  [root@pc-200 centoswp3]# podman run -d --net=host --name repositories centos:centoswp3
  225dd7fd411929b31d598c832d945b841c52f4a100ee1913a768249c8501a26e
  [root@pc-200 centoswp3]#

More secure, but less simple (need to specify ports to bind):

.. code-block:: bash

  [root@pc-200 ~]# podman run -d -p 80:80 --name repositories centos:centoswp3
  571eb6e50217d8bf6953353350587b37da0e783eb4b2c0893738cfd44f7db8a0
  [root@pc-200 ~]#

Both ways work.

.. note::
  80:80 means port 80 on the main host is mapped to port 80 of the
  container. If you want to use a different port on the host, you can select any
  available port. For example, 8080:80 would map the port 8080 of the host to the
  port 80 of the container.

Check the container is running:

.. code-block:: bash

  [root@pc-200 centoswp3]# podman ps -a
  CONTAINER ID  IMAGE                       COMMAND     CREATED        STATUS            PORTS  NAMES
  225dd7fd4119  localhost/centos:centoswp3  /sbin/init  4 seconds ago  Up 3 seconds ago         repositories
  [root@pc-200 centoswp3]#

Now create a simple playbook my_playbook.yml, that contains the following:

.. code-block:: yaml

  - hosts: repositories
    connection: podman
    tasks:
      - name: "package █ Install httpd packages"
        package:
          name: httpd
          state: present
        tags:
          - package
      - name: "service █ Manage httpd services state"
        service:
          name: httpd
          enabled: yes
          state: started
        tags:
          - service

Note the connection type, and that we specified the name of the target host, here the container name.

Now create a basic Ansible inventory with our container as an host:

.. code-block:: text

  mkdir my_inventory

And create my_inventory/my_containers with the following content:

.. code-block:: text

  repositories ansible_connection=podman ansible_python_interpreter=/usr/bin/python3

Now simply use ansible playbook to push configuration:

.. code-block:: bash

  [root@pc-200 ~]# ansible-playbook my_playbook.yml -i my_inventory

  PLAY [repositories] ************************************************************************************************

  TASK [Gathering Facts] *********************************************************************************************
  ok: [repositories]

  TASK [package █ Install httpd packages] ****************************************************************************
  changed: [repositories]

  TASK [service █ Manage httpd services state] ***********************************************************************
  changed: [repositories]

  PLAY RECAP *********************************************************************************************************
  repositories               : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

  [root@pc-200 ~]#

And check the httpd server from the container is running.

Here host is listening on 192.168.1.21:

.. code-block:: bash

  [root@pc-200 ~]# ip a
  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
      link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
      inet 127.0.0.1/8 scope host lo
         valid_lft forever preferred_lft forever
      inet6 ::1/128 scope host
         valid_lft forever preferred_lft forever
  3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
      link/ether XX:XX:XX:XX:XX:XX brd ff:ff:ff:ff:ff:ff
      inet 192.168.1.21/24 brd 192.168.1.255 scope global dynamic noprefixroute eth1
         valid_lft 64092sec preferred_lft 64092sec
  [root@pc-200 ~]#

Use a web browser to check http server is running (you will end up in apache test page).
