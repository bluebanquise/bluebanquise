FROM rockylinux/rockylinux:8

RUN set -ex; \
    dnf -y install python3 httpd procps less epel-release; dnf clean all;
RUN mkdir /root/.ssh -p;

CMD [ "/sbin/init" ]