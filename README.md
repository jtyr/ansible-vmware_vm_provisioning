vmware_vm_provisioning
======================

Ansible role which helps to provision VMs on VMware vCenter.

The configuration of the role is done in such way that it should not be
necessary to change the role for any kind of configuration. All can be
done either by changing role parameters or by declaring completely new
configuration as a variable. That makes this role absolutely
universal. See the examples below for more details.

Please report any issues or send PR.


Examples
--------

```yaml
---

- name: Example of how to provision VMs (all in one data structure)
  hosts: all
  connection: local
  gather_facts: no
  vars:
    # List of VMs to provision
    vmware_vm_provisioning_vms:
      # Fist VM
      - name: test01
        hostname: vcenter.example.com
        username: administrator@example.com
        password: p4ssw0rd
        validate_certs: no
        datacenter: DC1
        cluster: Cluster1
        folder: /DC1/vm
        template: CentOS-7-1525432016
        disks:
          - size_gb: 20
            autoselect_datastore: yes
        network:
          - name: VM Network
            ip: 192.168.1.178
            netmask: 255.255.255.0
            gateway: 192.168.1.1
        hadrware:
          num_cpus: 2
          memory_mb: 2048

      # Second VM
      - name: test02
        hostname: vcenter.example.com
        username: administrator@example.com
        password: p4ssw0rd
        validate_certs: no
        datacenter: DC2
        cluster: Cluster2
        folder: /DC2/vm
        template: CentOS-7-1525432016
        disks:
          - size_gb: 20
            autoselect_datastore: yes
          - size_gb: 500
            type: thin
            autoselect_datastore: yes
        network:
          - name: VM Network
            ip: 10.0.0.178
            netmask: 255.255.255.0
            gateway: 10.0.0.1
        hadrware:
          num_cpus: 2
          memory_mb: 16384
          nested_virt: yes

      # Third VM
      - name: test03
        hostname: vcenter.example.com
        username: administrator@example.com
        password: p4ssw0rd
        validate_certs: no
        datacenter: DC2
        cluster: Cluster2
        folder: /DC2/vm
        disks:
          - size_gb: 20
            autoselect_datastore: yes
          - size_gb: 500
            type: thin
            autoselect_datastore: yes
        network:
          - name: VM Network
            ip: 10.0.0.179
            netmask: 255.255.255.0
            gateway: 10.0.0.1
        hadrware:
          num_cpus: 2
          memory_mb: 16384
          nested_virt: yes
        # Special state implemented only by this role
        # It will power off, remove and create the VM
        state: rebuilt
  roles:
    - role: vmware_vm_provisioning
      tags: vmware_vm_provisioning
      when: >
        inventory_hostname == 'localhost'

- name: The same like above but with reusable variables
  hosts: all
  connection: local
  gather_facts: no
  vars:
    # Default login details
    vmware_vm_provisioning_hostname: vcenter.example.com
    vmware_vm_provisioning_username: administrator@example.com
    vmware_vm_provisioning_password: p4ssw0rd
    vmware_vm_provisioning_validate_certs: no

    # Default template
    vmware_vm_provisioning_template: CentOS-7-1525432016

    # Default HW configuration
    vmware_vm_provisioning_hardware: &vmware_vm_provisioning_hardware
      num_cpus: 2
      memory_mb: 2048

    # Disk configuration (size corresponds with the disk size from the template)
    vmware_vm_provisioning_disk__image: &vmware_vm_provisioning_disk__image
      size_gb: 5
      autoselect_datastore: yes

    # Default list of disks
    vmware_vm_provisioning_disk:
      - "{{ vmware_vm_provisioning_disk__image }}"

    # Network configuration for MyNET1
    vmware_vm_provisioning_networks__mynet1: &vmware_vm_provisioning_networks__mynet1
      - name: VM Network
        netmask: 255.255.255.0
        gateway: 192.168.1.1

    # Network configuration for MyNET1
    vmware_vm_provisioning_networks__mynet1: &vmware_vm_provisioning_networks__mynet2
      - name: VM Network
        netmask: 255.255.255.0
        gateway: 10.0.0.1

    # DC1 - Cluster1
    vmware_vm_provisioning__dc1_cluster1: &vmware_vm_provisioning__dc1_cluster1
      datacenter: DC1
      cluster: Cluster1
      folder: /DC1/vm

    # DC2 - Cluster2
    vmware_vm_provisioning__dc2_cluster2: &vmware_vm_provisioning__dc2_cluster2
      datacenter: DC2
      cluster: Cluster2
      folder: /DC2/vm

    # List of VMs to provision
    vmware_vm_provisioning_vms:
      # First VM
      - <<: *vmware_vm_provisioning__dc1_cluster1
        name: test01
        networks:
          # Include the default network configuration
          - <<: *vmware_vm_provisioning_networks__mynet1
            # And jsut add the IP
            ip: 192.168.1.178

      # Second VM
      - <<: *vmware_vm_provisioning__dc2_cluster2
        name: test02
        networks:
          # Include the default network configuration
          - <<: *vmware_vm_provisioning_networks__mynet2
            # And jsut add the IP
            ip: 10.0.0.178
        disks:
          # Include the default disk configuration
          - <<: *vmware_vm_provisioning_disk__image
          # Add one more disk (500G)
          - size_gb: 500
            type: thin
            autoselect_datastore: yes
        hardware:
          # Include the default hardware settings
          <<: *vmware_vm_provisioning_hardware
          # And override memory size
          memory_mb: 16384
          # And add one more additional option
          nested_virt: yes

      # Third VM
      - <<: *vmware_vm_provisioning__dc2_cluster2
        name: test03
        networks:
          # Different way of setting the IP
          - "{{ vmware_vm_provisioning_networks__mynet2 | combine({ 'ip': '10.0.0.179' }) }}"
        # Different way of adding an extra disk
        disks: "{{
          vmware_vm_provisioning_disk +
          [{ 'size_gb': 500,
             'type': 'thin',
             'autoselect_datastore': true }] }}"
        # Different way of setting the HW params
        hardware: "{{
          vmware_vm_provisioning_hardware | combine({
            'memory_mb': 16384,
            'nested_virt': true }) }}"
        # Special state implemented only by this role
        # It will power off, remove and create the VM
        state: rebuilt
  roles:
    - role: vmware_vm_provisioning
      tags: vmware_vm_provisioning
```

In order to provision only certain VMs, you can use the following approach:

```shell
ansible-playbook \
  # Inventory with the VMs we want to provision
  -i hosts \
  # Limit execution only for VMs test01 and test03
  -l '~test0[13]' \
  # The name of the playbook from the examples above
  vm_provisioning.yaml
```

We can also use execute Ansible with multiple playbooks to configure the VM
right after it was provisioned:

```shell
ansible-playbook \
  -i hosts \
  -l '~test0[13]' \
  vm_provisioning.yaml \
  # That's the second playbook which configures the provisioned VM(s)
  site.yaml
```


Role variables
--------------

```yaml
# Whether to show logs or not
vmware_vm_provisioning_force_show_log: no

# List of VMs to provision (see README for details)
vmware_vm_provisioning_vms: []

# Default values (see README for details)
#vmware_vm_provisioning_annotation: null
#vmware_vm_provisioning_cdrom: null
#vmware_vm_provisioning_cluster: null
#vmware_vm_provisioning_customization: null
#vmware_vm_provisioning_customization_spec: null
#vmware_vm_provisioning_customvalues: null
#vmware_vm_provisioning_datacenter: null
#vmware_vm_provisioning_disk: null
#vmware_vm_provisioning_esxi_hostname: null
#vmware_vm_provisioning_folder: null
#vmware_vm_provisioning_force: null
#vmware_vm_provisioning_guest_id: null
#vmware_vm_provisioning_hardware: null
#vmware_vm_provisioning_hostname: null
#vmware_vm_provisioning_is_template: null
#vmware_vm_provisioning_linked_clone: null
#vmware_vm_provisioning_name_match: null
#vmware_vm_provisioning_networks: null
#vmware_vm_provisioning_password: null
#vmware_vm_provisioning_port: null
#vmware_vm_provisioning_resource_pool: null
#vmware_vm_provisioning_snapshot_src: null
#vmware_vm_provisioning_state_change_timeout: null
#vmware_vm_provisioning_state: null
#vmware_vm_provisioning_template: null
#vmware_vm_provisioning_username: null
#vmware_vm_provisioning_uuid: null
#vmware_vm_provisioning_validate_certs: null
#vmware_vm_provisioning_vapp_properties: null
#vmware_vm_provisioning_wait_for_ip_address: null
```


License
-------

MIT


Author
------

Jiri Tyr
