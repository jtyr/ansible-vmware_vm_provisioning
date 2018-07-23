vmware_vm_provisioning
======================

Ansible role which helps to provision VMs on VMware vCenter/ESXi.

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
  roles:
    - vmware_vm_provisioning

- name: The same like above but with reusable variables
  hosts: all
  vars:
    # Default login details
    vmware_vm_provisioning_hostname: vcenter.example.com
    vmware_vm_provisioning_username: administrator@example.com
    vmware_vm_provisioning_password: p4ssw0rd
    vmware_vm_provisioning_validate_certs: no

    # Disk configuration
    vmware_vm_provisioning_disks__default: &vmware_vm_provisioning_disks__default
      size_gb: 20
      autoselect_datastore: yes

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

    # Default HW configuration
    vmware_vm_provisioning_hardware: &vmware_vm_provisioning_hardware
      num_cpus: 2
      memory_mb: 2048

    # Default template
    vmware_vm_provisioning_template: CentOS-7-1525432016

    # List of VMs to provision
    vmware_vm_provisioning_vms:
      # First VM
      - name: test01
        datacenter: DC1
        cluster: Cluster1
        folder: /DC1/vm
        networks:
          # Include the default network configuration
          - <<: *vmware_vm_provisioning_networks__mynet1
            # And jsut add the IP
            ip: 192.168.1.178
        disks:
          # Include the default disk configuration
          - <<: *vmware_vm_provisioning_disks__default

      # Second VM
      - name: test02
        datacenter: DC2
        cluster: Cluster2
        folder: /DC2/vm
        networks:
          # Include the default network configuration
          - <<: *vmware_vm_provisioning_networks__mynet2
            # And jsut add the IP
            ip: 10.0.0.178
        disks:
          # Include the default disk configuration
          - <<: *vmware_vm_provisioning_disks__default
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
  roles:
    - vmware_vm_provisioning
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
