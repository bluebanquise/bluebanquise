FROM centos

RUN set -ex; \
    dnf -y install python3; dnf clean all; \
    dnf -y install epel-release; \
    dnf -y install ansible; \
    mkdir -p /var/www/html/repositories/centos/8/x86_64/os/; \
    mkdir -p /var/www/html/repositories/centos/8/x86_64/os/bluebanquise/;

RUN { \
    echo "[bluebanquise]"; \
    echo "name=bluebanquise"; \
    echo "baseurl=http://bluebanquise.com/repository/releases/latest/el8/x86_64/bluebanquise/"; \
    echo "gpgcheck=0"; \
    echo "enabled=1"; \
    } > /etc/yum.repos.d/bluebanquise.repo

RUN set -ex; \
    dnf -y install bluebanquise; \
    dnf -y install openssh openssh-server openssh-clients; \
    echo 'Port 2222' >> /etc/ssh/sshd_config; \
    systemctl enable sshd; \
    ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P ""; \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys; \
    ssh-keygen -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key; \
    ssh-keygen -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key; \
    ssh-keygen -N "" -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key; \
    echo 'localhost,127.0.0.1 '$(cat /etc/ssh/ssh_host_ecdsa_key.pub) > /root/.ssh/known_hosts; \
    echo '[management1]:2222 ecdsa-sha2-nistp256 '$(cat /etc/ssh/ssh_host_ecdsa_key.pub | awk -F ' ' '{print $2}') >> /root/.ssh/known_hosts; \
    cp -a /usr/share/doc/bluebanquise/examples/simple_cluster/* /etc/bluebanquise/; \
    rm -Rf /etc/bluebanquise/inventory/cluster/*; \
    mkdir /etc/bluebanquise/inventory/cluster/nodes/; \
    rm -f /etc/bluebanquise/inventory/group_vars/all/equipment_all/authentication.yml; \
    rm -f /etc/bluebanquise/inventory/group_vars/equipment_typeM/equipment_profile.yml;

RUN { \
    echo '---'; \
    echo 'ep_access_control: disabled'; \
    echo 'ep_firewall: false'; \
    } > /etc/bluebanquise/inventory/group_vars/equipment_typeM/equipment_profile.yml

RUN { \
    echo '---'; \
    echo 'authentication_root_password_sha512: $6$M3crarMVoUV3rALd$ZTre2CIyss7zOb4lkLoG23As9OAkYPw2BM88Y1F43n8CCyV5XWwAYEwBOrS8bcCBIMjIPdJG.ndOfzWyAVR4j0 # This password is "root", change it!'; \
    echo 'authentication_ssh_keys:'; \
    echo '  - '$(cat /root/.ssh/id_rsa.pub); \
    } > /etc/bluebanquise/inventory/group_vars/all/equipment_all/authentication.yml

RUN { \
    echo 'mg_managements:'; \
    echo '  children:'; \
    echo '    equipment_typeM:'; \
    echo '      hosts:'; \
    echo '        management1:'; \
    echo '          ansible_port: 2222'; \
    echo '          network_interfaces:'; \
    echo '            - interface: generic'; \
    echo '              ip4: 10.10.0.1'; \
    echo '              network: ice1-1'; \
    echo '              mac: 08:00:27:dc:f8:f5'; \
    } > /etc/bluebanquise/inventory/cluster/nodes/managements.yml

CMD [ "/sbin/init" ]
