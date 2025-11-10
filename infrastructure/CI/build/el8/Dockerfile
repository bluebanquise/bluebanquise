FROM docker.io/rockylinux/rockylinux:8
RUN dnf install git -y
RUN mkdir /infra
RUN git clone https://github.com/bluebanquise/infrastructure.git /infra
RUN chmod +x /infra/auto_builder.sh
RUN /infra/auto_builder.sh dependencies RedHat 8
ENTRYPOINT ["/infra/auto_builder.sh"]
