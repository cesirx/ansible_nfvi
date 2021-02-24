# Host_Management

A set of Ansible playbooks and roles to manage different layers of a NFVI infrastructure: ESXi, iLO, iDRAC...

# Repo structure

<pre>

.
├── README.md
├── build_ansible_inventory.py
├── dell
│   └── playbooks
│       ├── disable_IPMILan.yml
│       ├── group_vars -> ../../group_vars/
│       ├── hosts_pro -> ../../hosts_pro
│       ├── manage_idrac_users.yml
│       ├── racadm_update.yml
│       ├── update_bios.yml
│       └── update_idrac.yml
├── esxi
│   └── playbooks
│       ├── group_vars -> ../../group_vars/
│       ├── hosts_pro -> ../../hosts_pro
│       ├── manage_esxi_cli_users.yml
│       ├── roles
│       │   ├── change_esxi_cli_user_pass
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── create_esxi_cli_user
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── delete_esxi_cli_user
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── esxi_reboot
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── get_i40en_version
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── hostd_reboot
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── list_esxi_cli_users
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── postchecks
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── prechecks
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   ├── set_trust_vector
│       │   │   └── tasks
│       │   │       └── main.yml
│       │   └── vib_install
│       │       └── tasks
│       │           └── main.yml
│       └── update_intel_x710_driver.yml
├── generic
│   └── playbooks
│       ├── disable_IPMILan.yml
│       ├── group_vars -> ../../group_vars/
│       ├── hosts_pro -> ../../hosts_pro
│       ├── known_hosts.yml
│       └── ssh_key_push.yml
├── group_vars
│   ├── all
│   ├── hp_all
│   ├── production
│   └── production_r740_all
├── hosts_pro
└── hp
    └── playbooks
        ├── group_vars -> ../../group_vars/
        ├── hosts_pro -> ../../hosts_pro
        ├── manage_ilo_users.yml
        ├── roles
        │   ├── change_ilo_user_pass
        │   │   └── tasks
        │   │       └── main.yml
        │   ├── create_ilo_users
        │   │   └── tasks
        │   │       └── main.yml
        │   ├── delete_ilo_users
        │   │   └── tasks
        │   │       └── main.yml
        │   └── list_ilo_users
        │       └── tasks
        │           └── main.yml
        └── update_ilo.yml

</pre>

# Example
`ansible-playbook update_intel_x710_driver.yml -i hosts_pro --ask-vault-pass --extra-vars "variable_host=datacenter_a"`

