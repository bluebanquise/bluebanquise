FROM docker.io/opensuse/leap:15
RUN zypper -n install git 
RUN mkdir /infra
RUN git clone https://github.com/bluebanquise/infrastructure.git /infra
RUN chmod +x /infra/auto_builder.sh
RUN /infra/auto_builder.sh dependencies opensuse_leap 15
ENTRYPOINT ["/infra/auto_builder.sh"]
