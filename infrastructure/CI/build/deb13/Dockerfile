FROM docker.io/debian:13
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install -y git systemd-sysv systemd
RUN mkdir /infra
RUN git clone https://github.com/bluebanquise/infrastructure.git /infra
RUN chmod +x /infra/auto_builder.sh
RUN /infra/auto_builder.sh dependencies Debian 13
ENTRYPOINT ["/infra/auto_builder.sh"]
