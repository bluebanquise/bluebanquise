FROM docker.io/ubuntu:24.04
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git systemd-sysv systemd
RUN mkdir /infra
RUN git clone https://github.com/bluebanquise/infrastructure.git /infra
RUN chmod +x /infra/auto_builder.sh
RUN /infra/auto_builder.sh dependencies Ubuntu 24.04
ENTRYPOINT ["/infra/auto_builder.sh"]
