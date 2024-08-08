# Automate

## Instructions

### Anticipate dependencies

The automate tool need few python dependencies to be available 
in the host active repositories.

On CentOS 8 based systems, activate EPEL and RabbitMQ dedicated repositories:

```
dnf install -y epel-release
dnf install -y centos-release-rabbitmq-38
```

### Create tasks list

The tool expects a task list to be provided.

Create file `/etc/bbautomate/tasks.yml`, and define your tasks the following way:

```yaml
deploy_computes_nodes:
  - name: bootset and reboot
    tasks:
      - command: '"bootset -b osdeploy -n " + task_data["node"]'
        timeout: 10
      - command: '"powerman --cycle " + task_data["node"]'
      - action: wait
        delay: 10
        comment: we wait for the node to be rebooted before starting next task
  - name: Wait for ssh connectivity
    tasks:
      - action: ssh_wait
        delay: 20
    retry: 10
  - name: Deploy playbook once node is back
    tasks:
      - command: '"ANSIBLE_CONFIG=/etc/bluebanquise/ansible.cfg ansible-playbook /etc/bluebanquise/playbooks/" + task_data["playbook"] + ".yml --limit " + task_data["node"]'
```

This `deploy_computes_nodes` task allows to automate nodes deployment.

The task is split in multiple sub-tasks, each containing a list of dedicated commands/actions to perform.

There are 2 actions available for now in the tool:

* wait: to be combined with delay value. A simple sleep in seconds.
* ssh_wait: to be combined with delay value. This action wait for an host to expose ssh connectivity.

Each sub-task can be retried multiple time using the retry key. When a task fails, it will be scheduled again by the automate if retry count limit is not reached.

**Important**: each time this file is updated, both automate services need to be restarted to take changes into account:

```
systemctl restart bbautomate_celery
systemctl restart bbautomate_flask
```

### Logs

Global logs can be found in `/var/log/bluebanquise/automate/global.log`.
When a task is performed with a specific target node as argument (assuming here 'mynode'), logs can be found in 
`/var/log/bluebanquise/automate/mynode.log`.

### Triggering tasks

The tool listens via Flask on port **5000** on **localhost**.

To trigger a task, for example `deploy_computes_nodes` seen above, query the Flask server via a curl command:

```
curl -X PUT -H 'Content-Type: application/json' http://localhost:5000/start_task -d '{"task": "deploy_computes_nodes", "playbook": "computes", "node": "mynode"}'
```

URL is `http://localhost:5000/start_task`, and task to be triggered is provided as JSON argument.
Other JSON parameters are users custom parameters that can be seen in the task commands. For example, command:

```
      - command: '"bootset -b osdeploy -n " + task_data["node"]'
```

Will be performed as following, considering curl arguments:

```
bootset -b osdeploy -n mynode
```

This way, users can defined sophisticated tasks, using arguments passed at call as JSON arguments.

### Diskless

The diskless role can be combined with this automate to allow auto diskless nodes provisioning at boot.

To achieve that, simply create the following task in `/etc/bbautomate/tasks.yml`:

```yaml
configure_diskless_nodes:
  - name: Wait for ssh connectivity
    tasks:
      - action: ssh_wait
        delay: 10
    retry: 4
  - name: Deploy playbook once node ssh connectivity is ready
    tasks:
      - command: '"ANSIBLE_CONFIG=/etc/bluebanquise/ansible.cfg ansible-playbook /etc/bluebanquise/playbooks/diskless.yml --limit " + task_data["node"]'
```

Then, inside node diskless image, create the following file `/request_playbook.sh`:

```
#!/bin/bash

# Turn the kernel parameters into variables
# We are looking for node_hostname provided during iPXE process
set -- `cat /proc/cmdline`
for I in $*; do case "$I" in *=*) eval $I;; esac; done

command="curl --connect-timeout 20 --max-time 400 -X PUT -H 'Content-Type: application/json' http://management1:5000/start_task -d '{\"task\": \"deploy_computes_nodes\", \"node\": \"$node_hostname\"}'"
eval $command
```

And make it executable:

```
chmod +x /request_playbook.sh
```

Then create the associated service file `/etc/systemd/system/startup_playbook.service`:

```
[Unit]
Description=Startup Playbook
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/request_playbook.sh
RemainAfterExit=true
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Then reload systemctl and enable it:

```
systemctl daemon-reload
systemctl enable startup_playbook
```

And repack diskless image.

Once booted, diskless nodes will now trigger the automate to request a playbook execution.

## Changelog

* 1.0.1: Improve yaml loader. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>

