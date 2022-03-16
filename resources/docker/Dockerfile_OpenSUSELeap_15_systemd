FROM opensuse/leap:15

RUN set -ex; \
     zypper -n install python3 systemd-sysvinit systemd-network;
RUN mkdir /root/.ssh -p;

CMD [ "/sbin/init" ]