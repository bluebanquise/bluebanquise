keepalived_vrrp_instances:
  -  name: VI_1
    *interface: enp0s3
     id:
     state:
     priority:
     advert_int:
     additional_parameters:
       tutu: toto
    *auth_pass: secret
    *virtual_ipaddress:
       - 10.10.0.3/16 brd 10.10.255.255 scope global
    manage_haproxy:
