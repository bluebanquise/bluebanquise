# Generic wrappers collection

![generic](generic_logo.svg)

This roles is just a convenient collection of wrappers above the following Ansible modules:

* cron
* package
* file
* template
* service
* lineinfile
* filesystem

Using this role, it is theoretically possible to setup and start a large number of services.

## Wrappers

### cron

Set needed cron on node/group by defining generic.cron list based on cron module parameters. Example:

```yaml
generic:
  cron:
    - name: "check dirs"
      minute: "0"
      hour: "5,2"
      job: "ls -alh > /dev/null"
    - name: yum autoupdate
      weekday: "2"
      minute: "0"
      hour: "12"
      user: root
      job: "YUMINTERACTIVE=0 /usr/sbin/yum-autoupdate"
      cron_file: ansible_yum-autoupdate
```

See `**cron** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/cron_module.html>`_
for the full list of available parameters.

### package

Install desired packages on node/group by defining generic.package list based on package module parameters. Example:

```yaml
generic:
  package:
    - name: ntpdate
      state: present
    - name: "{{ apache }}"
      state: absent
```

See `**package** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html>`_
for the full list of available parameters.

### file

Create desired file or folder / change permissions / etc on node/group by defining generic.file list based on file module parameters. Example:

```yaml
generic:
  file:
    - path: /etc/foo.conf
      owner: foo
      group: foo
      mode: '0644'
    - src: /file/to/link/to
      dest: /path/to/symlink
      owner: foo
      group: foo
      state: link
    - path: /etc/some_directory
      state: directory
      mode: '0755'
```

See `**file** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html>`_
for the full list of available parameters.

### template

Generate desired files based from custom templates on node/group by defining generic.template list based on template module parameters. Note that for this wrapper, a special additional key was added: `template`, that should contain the template to render and replace the `src` key:

```yaml
generic:
  template:
    - template: |
        This is a template to render
        {% for stuff in customlist %}
           {{ stuff }}
        {% endfor %}
      dest: /etc/file.conf
      owner: bin
      group: wheel
      mode: '0644'
```

See `**template** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html>`_
for the full list of available parameters.

### lineinfile

Edit lines of files on node/group by defining generic.lineinfile list based on lineinfile module parameters. Example:

```yaml
generic:
  lineilfile:
    - path: /etc/selinux/config
      regexp: '^SELINUX='
      line: SELINUX=enforcing
    - path: /etc/hosts
      regexp: '^127\.0\.0\.1'
      line: 127.0.0.1 localhost
      owner: root
      group: root
      mode: '0644'
```

See `**lineinfile** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html>`_
for the full list of available parameters.

### service

Manage services on node/group by defining generic.service list based on service module parameters. Example:

```yaml
generic:
  service:
    - name: httpd
      state: started
    - name: network
      state: restarted
      args: eth0
```

See `**service** Ansible module page <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html>`_
for the full list of available parameters.

## filesystem

Manage filesystems (devices or files) on node/group by defining generic.filesystem list based on filesystem module parameters. Example:

```yaml
generic:
  filesystem:
    - fstype: ext2
      dev: /dev/sdb1
    - fstype: ext4
      dev: /dev/sdb1
      opts: -cc
    - dev: /dev/sde1
      state: absent
```

See `**filesystem** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/filesystem_module.html>`_
for the full list of available parameters.

## modprobe

Manage kernel modules on node/group by defining generic.modprobe list based on modprobe module parameters. Example:

```yaml
generic:
  modprobe:
    - name: 8021q
      state: present
    - name: dummy
      state: present
      params: 'numdummies=2'
```

See `**modprobe** Ansible module page <https://docs.ansible.com/ansible/latest/collections/community/general/modprobe_module.html>`_
for the full list of available parameters.

## Changelog

* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
