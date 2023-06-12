
Example playbook:

```YAML
---
- name: haproxy
  hosts: "mg_khap"
  become: true
  vars:
    keepalived_vrrp_instances:
      - name: VI_1
        interface: enp0s3
        id: 100
        state: MASTER
        priority: 100
        advert_int: 1
        additional_parameters: {}
        auth_pass: "<replace me>"
        virtual_ipaddress:
          - 10.10.0.3/16 brd 10.10.255.255 scope global
        manage_haproxy: true
  roles:
    - role: bluebanquise.high_availability.keepalived
      tags: keepalived
```

