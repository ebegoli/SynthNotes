Ansible
---

Installation, configuration, and execution in a unified self-documenting 
language.

# Requirements
- Python >= 2.7
- Ansible >= 2.4.2
- Jinja2 >= 2.9


# Getting started

1. Create a VM instance called `ansible` or `ansible-controller`. 
You can pick a flavor with more cores if you're going to be interacting 
with a lot of ansible hosts. Make sure you set up the `ssh` key from Horizon.
1. `ssh` into the `ansible` node with using the SSH key that you set up. 
The easiest way to make everything work is to use `ssh-agent` from you local terminal

```
eval "$(ssh-agent)"
ssh-add ~/.ssh/{id_rsa, code_rsa}
```
`code_rsa` is a key I set up for accessing the `code.ornl` GitLab key.
1. Clone the `benchmarking_infrastructure` repo onto `ansible`.
1. `cd benchmarking_infrastructure/ansible`


## Using ansible

The [ansible documentation](http://docs.ansible.com/ansible/latest/index.html)
is very good. Basically, you can run *ad-hoc* tasks such as 

```bash
ansible -i inventories/staging/hosts -a 'hostname' -m shell
```

where `staging` is a YAML file listing hostnames for specific hosts and/or 
groups of hosts, the *module* to run is `shell`, and the arguments to the
`shell` module is simply `hostname`. For more complicated workflows,
tasks can be assembled into playbooks and can be executed with, e.g.

```bash
ansible-playbook -i inventories/staging/hosts playbooks/elasticsearch/start-elasticsearch.yml
```

## Using vault

[Vault](http://docs.ansible.com/ansible/2.4/vault.html) 
is Ansible's mechanism for encrypting secrets. See the documentation for 
how to edit files and set up a password. We will follow the convention
that `vars` files will reference a companion `vault` file, and encrypted
variables will be prefixed with `vault`, e.g.
```yaml
openstack_password: "{{ vault_openstack_password }}"
```

If your role uses `localhost`, you will need to provide your vault password, since
the file `host_vars/localhost/vault` contains encrpyted secrets. Right now
these secrets are just your authorization for OpenStack. To give ansible your
vault password:

```bash
ansible-playbook -i inventories/staging openstack-start.yml --ask-vault-pass
```

If you tire of entering your password, ansible can pass it as a file or script:

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=~/path/to/vault_pass.txt
ansible-playbook -i staging openstack-start.yml
```

## Using dynamic inventory

[docs](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html#using-inventory-directories-and-multiple-inventory-sources)

To propagate `group_vars` and `host_vars`.

```bash
ansible-playbook -i inventories/dynamic <playbook.yml>
```

## Role layout

Tasks within a role are grouped into three broad categories: common (installation),
configuration, and execution (starting/stopping servers, e.g.). The common
tasks are to be included in the `uber-server` or `uber-client` such that they
don't need to be repeated when spinning up clusters. The configuration tasks
allow us to inject configuration parameters into the setup, and execution 
operates under a given configuration, so these last two categories should not
be executed by the `uber-` VMs. Roles that do not follow this pattern are
`common`, `anaconda`, `python-client`, and `utils`.

## Using Ansible for configuration

Ansible is a configuration management system written in Python. The end-user
specifies the desired configuration state of a host through the use of YML 
markdown
files. Ansible communicates with remote servers using SSH.

Ansible supports the Jinja2 templating language for dynamic configuration. 
This means
that configuring for different Unix OS's can be greatly simplified with logical
switches. Perhaps more importantly, the hostnames of the servers 
to be used in the
cluster can be changed from a single toplevel configuration file.

Cloudera Manager and Ambari are the popular Hadoop ecosystem management tools,
but for the purposes of research, these two solutions are nearly intractable.
These enterprise management tools are slow to adopt new software versions, they
are rather inflexible with respect to custom software in general. 
In Cloudera Manager,
for example, in order to use a non-standard piece of software, 
the user is required
to create a custom parcel for the software itself and to create a Custom Service
Descriptor for any daemons that the software needs. Creating CSDs is cumbersome,
difficult to debug, and overall poorly supported.

### Inventory

Inventory specifies the hosts on which to execute ansible tasks. 

Example inventory file:

```
namenode ansible_host=172.22.3.179
alluxio_master ansible_host=172.22.3.179
hbase_master ansible_host=172.22.3.179

standby_namenode ansible_host=172.22.3.180
hbase_backup_master ansible_host=172.22.3.180

[datanodes]
172.22.3.[189:193]

[alluxio_workers]
172.22.3.[189:193]

[regionservers]
172.22.3.[189:193]

[zookeepers]
172.22.3.[191:193]
```


### Roles

Roles allow a complex setup to be factored into smaller, more manageable parts.
The concepts of roles map well to the daemons used in most Hadoop-ecosytem 
projects.

```bash
├── yarn-nodemanager
├── yarn-resourcemanager
└── zookeeper-server
```

Roles encapsulate the logic necessary to complete a set of closely related *tasks*,
the fundamental unit of ansible *playbooks*. Here, we've organized instances
into individual playbooks (`hdfs.yml`, `hbase.yml`).

```bash
common
├── defaults
│   └── main.yml
├── handlers
├── meta
├── tasks
│   ├── groups.yml
│   ├── hdfs.yml
│   ├── hosts.yml
│   ├── java.yml
│   ├── main.yml
│   └── users.yml
├── templates
│   ├── etc
│   │   └── hosts.j2
│   ├── hdfs.sh.j2
│   └── java_home.sh.j2
└── vars
```

### Delegating roles


### Global variables

The file `group_vars/all` contains the global variables made available to every
host in the inventory. This is the logical place to store configurations common
to multiple roles, for instance available memory.

### Best practices

In the development phase, it is tempting to bypass ansible for starting daemons, 
etc., but since ansible only checks the state of a system, it is easy to omit a 
key step in the process. In other words, it is the burden of the ansible user 
to ensure that the sequence of tasks executed actually leads to the desired 
state. This is important
for both new environments and currently running environments 
(i.e. during rolling upgrades).

![scenarios](figures/scenarios.png)
