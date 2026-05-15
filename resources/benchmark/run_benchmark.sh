set -x
set -e

# Gen inventory
./gen_inventory.sh
# Move to repo top
cd ../../

# Build image for tests
docker build -t ubuntu_24:systemd -f ./resources/docker/Dockerfile_Ubuntu_24_systemd .
sudo modprobe -v dummy numdummies=2 && sudo ip addr add 10.10.250.1/16 dev dummy0 && sudo ip addr add 10.11.250.1/16 dev dummy0 && sudo ip link set dev dummy0 up && ip a;
echo -e 'bb_repositories:\n  - name: bluebanquise\n    repo: "deb [trusted=yes] https://bluebanquise.com/repository/releases/latest/u24/x86_64/bluebanquise/ noble main"' > resources/workflow/inventory_standard/group_vars/all/repositories.yml
docker run -d --privileged --cgroupns=host --net=host --name mgt1 -v /sys/fs/cgroup:/sys/fs/cgroup:rw -v $PWD:/bluebanquise ubuntu_24:systemd
docker exec mgt1 bash -c "/bluebanquise/bootstrap/online_bootstrap.sh --silent --skip_environment"
docker exec mgt1 bash -c "sudo -u bluebanquise /bin/bash -c 'cd /bluebanquise/bootstrap/ && ./configure_environment.sh --bb_collections_local_path=/bluebanquise/collections/'"
docker exec mgt1 bash -c "apt update && DEBIAN_FRONTEND=noninteractive apt-get install apt-utils python3-apt -y"
docker exec mgt1 bash -c "sudo -u bluebanquise /bin/bash -c 'cp -a /bluebanquise/resources/benchmark/inventory_large /var/lib/bluebanquise/inventory && cp -a /bluebanquise/resources/benchmark/playbook.yml /var/lib/bluebanquise'"
docker exec mgt1 bash -c "sudo -u bluebanquise /bin/bash -c 'source /var/lib/bluebanquise/ansible_venv/bin/activate && ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.infrastructure.core ansible-playbook /var/lib/bluebanquise/playbook.yml -i /var/lib/bluebanquise/inventory --become --connection=local --limit mgt1 --diff --tags repositories'"

# Ready to bench.
# Store EPOCH
t_start=$(date +%s)
docker exec mgt1 bash -c "sudo -u bluebanquise /bin/bash -c 'source /var/lib/bluebanquise/ansible_venv/bin/activate && ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.infrastructure.core ansible-playbook /var/lib/bluebanquise/playbook.yml -i /var/lib/bluebanquise/inventory --become --connection=local --limit mgt1 --diff --check --tags hosts_file'"
docker exec mgt1 bash -c "sudo -u bluebanquise /bin/bash -c 'source /var/lib/bluebanquise/ansible_venv/bin/activate && ANSIBLE_JINJA2_EXTENSIONS=jinja2.ext.loopcontrols,jinja2.ext.do ANSIBLE_VARS_ENABLED=ansible.builtin.host_group_vars,bluebanquise.infrastructure.core ansible-playbook /var/lib/bluebanquise/playbook.yml -i /var/lib/bluebanquise/inventory --become --connection=local --limit mgt1 --diff --tags dhcp_server,dns_server'"
t_infra=$(date +%s)

echo
echo "Benchmark results"
echo $t_start $t_infra
