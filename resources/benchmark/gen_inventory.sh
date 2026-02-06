
c_size=4
n_size=250
rm -Rf inventory_large
mkdir -p inventory_large/
echo -e "all:\n  hosts:\n" > inventory_large/hosts.yml
cat << EOF >> inventory_large/hosts.yml
    mgt1:
      network_interfaces:
        - interface: eno1
          ip4: 10.10.250.1
          network: net-admin
        - interface: ib0
          ip4: 10.20.250.1
          network: interconnect
EOF
for (( c=1; c<=$c_size; c++ ))
do
  echo "Step $c/$c_size"
  for (( n=1; n<=250; n++))
  do
    nnode=$(((c-1)*250+n))
cat << EOF >> inventory_large/hosts.yml
    c$nnode:
      alias: foobar$nnode
      bmc:
        name: bc$nnode
        ip4: 10.11.$c.$n
        network: net-bmc
      network_interfaces:
        - interface: eno1
          ip4: 10.10.$c.$n
          network: net-admin
        - interface: ib0
          ip4: 10.20.$c.$n
          network: interconnect
EOF
  done
done

cat << EOF > inventory_large/groups
[fn_management]
mgt1
[fn_compute]
c[1:$((c_size*250))]

[os_ubuntu]
mgt1
c[1:$((c_size*250))]

[hw_A]
mgt1

[hw_B]
c[1:$((c_size*250))]
EOF

mkdir -p inventory_large/group_vars/all/
mkdir -p inventory_large/group_vars/os_ubuntu/
mkdir -p inventory_large/group_vars/hw_A/
mkdir -p inventory_large/group_vars/hw_B/

echo "hw_equipment_type: server" > inventory_large/group_vars/hw_A/main.yml
echo "hw_equipment_type: server" > inventory_large/group_vars/hw_B/main.yml

cat << EOF > inventory_large/group_vars/os_ubuntu/main.yml
os_operating_system:
  distribution: "ubuntu"
  distribution_version: "24.04"
  distribution_major_version: "24"
EOF

cat << EOF > inventory_large/group_vars/all/main.yml
bb_domain_name: cluster.local

networks:
  net-admin:
    subnet: 10.10.0.0
    prefix: 16
    services_ip: 10.10.250.1
  net-bmc:
    subnet: 10.11.0.0
    prefix: 16
    services_ip: 10.11.250.1
  interconnect:
    subnet: 10.20.0.0
    prefix: 16
EOF
