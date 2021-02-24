## Build Ansible invenotiry file from vCenter
#
## by Cesar Ortega (cesar.ortegaroman@telefonica.com)

from pyVmomi import vim     # Module "pyVmomi" to connect to vSphere API
from pyVim.connect import SmartConnect, Disconnect
import ssl
import argparse
import getpass
import pandas as pd
import os
import re
import socket

def parse_arguments():
    """Process input arguments."""

    parser = argparse.ArgumentParser()
    parser.add_argument('vcenter_ip', help='vCenter ip/fqdn')
    parser.add_argument('vcenter_user', help='vCenter login username')

    return parser.parse_args()

def connect(vcenter_ip, vcenter_user, vcenter_password):
    """Connect to vCenter and bypass SSL warnings.

    Parameters
    ----------
    vcenter_ip : string
        vCenter IP address or resolvable FQDN
    vcenter_user : string
        vCenter username (must have at least read privileges)
    vcenter_password : string
        vCenter password  

    Returns
    -------
    c
        vCenter Service Instance connection
    """

    #s = ssl.SSLContext(ssl.PROTOCOL_TLSv1) vCenter 6.7 disables TLS1.0
    s = ssl.SSLContext(ssl.PROTOCOL_TLS)    # Negotiate most recent TLS version between client and server
    s.verify_mode = ssl.CERT_NONE
    try:
        c = SmartConnect(host=vcenter_ip, user=vcenter_user, pwd=vcenter_password)
        #print ('Valid cert')
    except:
        c = SmartConnect(host=vcenter_ip, user=vcenter_user, pwd=vcenter_password, sslContext=s)
        #print ('Invalid or untrusted cert')
    return c

def get_obj(content, vimtype, name = None):
    """Return vCenter objects matching a given type.
    
    Parameters
    ----------
    content : pyVmomi.VmomiSupport.vim.ServiceInstanceContent
        connection to VMware vCenter
    vimtype : string
       pyvmomi object type to look for: VMs "[vim.VirtualMachine]", hosts "[vim.ComputeResource]", clusters "[vim.ClusterComputeResource]", etc. (per object name can be obtained from vCenter MOB URL)

    Results
    -------
    list
        list of vCenter object matching the given type
    """

    #content.rootFolder  --> starting point to look into
    #[vim.VirtualMachine]  -->   object types to look for
    #recursive  -->  whether we should look into it recursively
    return [item for item in content.viewManager.CreateContainerView(content.rootFolder, [vimtype], recursive=True).view]

def get_hosts(content):

    return [host_obj for host_obj in get_obj(content, vim.HostSystem)]

def get_hosts_data(content, df_hosts):

    hostobj_list = get_hosts(content)

    for host in hostobj_list:
        hostfqdn = host.name
        vendor = host.hardware.systemInfo.vendor.split(' ')[0].lower()
        model = host.hardware.systemInfo.model.split(' ')[1].lower()
        cluster = host.parent.name
        pop = cluster.split('_')[1].lower()
        if "bc" in hostfqdn:
            ipmifqdn = hostfqdn.replace('hv', 'bs')
        else:
            ipmifqdn = hostfqdn.replace('hv', 'rs')

        try:
            ipmiip = socket.gethostbyname(ipmifqdn)
        except:
            ipmiip = ""
        
        if "hp" in vendor:
            ipmivar = "ilo_ip"
        elif "dell" in vendor:
            ipmivar = "idrac_ip"

        df_hosts = df_hosts.append({'hostfqdn': hostfqdn, 'vendor': vendor,
                     'model': model, 'cluster': cluster, 'pop': pop, 
                     'ipmifqdn': ipmifqdn, 'ipmiip': ipmiip,'ipmivar': ipmivar}, ignore_index=True)

    return df_hosts

def print_dict(dictionary):

    string = '\n'
    for key, value in dictionary.items():
        string += '{}\n'.format(key)
        for item in value:
            string += '{}\n'.format(item)
        string += '\n'

    return string

def build_group(df_hosts):

    env = ''
    title = ''
    children_grp = ''
    inventory_string = ''

    children_dict = {}
    pop_children_dict = {}
    vendor_children_dict = {}
    model_children_dict = {}
    
    grp = df_hosts.groupby(['pop', 'model', 'vendor'])
    #print(grp.groups.keys())
    for key in grp.groups.keys():
        children_dict.setdefault(f'[{key[0]}_{key[2]}:children]', []).append(f'{key[0]}_{key[1]}')
        if (f'[{key[0]}:children]' not in pop_children_dict) or (f'{key[0]}_{key[2]}' not in pop_children_dict[f'[{key[0]}:children]']):
            pop_children_dict.setdefault(f'[{key[0]}:children]', []).append(f'{key[0]}_{key[2]}')
        if (f'[{key[2]}_all:children]' not in vendor_children_dict) or (f'{key[0]}_{key[2]}' not in vendor_children_dict[f'[{key[2]}_all:children]']):   
            vendor_children_dict.setdefault(f'[{key[2]}_all:children]', []).append(f'{key[0]}_{key[2]}')
        if (f'[{key[1]}_all:children]' not in vendor_children_dict) or (f'{key[0]}_{key[1]}' not in vendor_children_dict[f'[{key[1]}_all:children]']):   
            model_children_dict.setdefault(f'[{key[1]}_all:children]', []).append(f'{key[0]}_{key[1]}')

    if 'maddv' in df_hosts['pop']:
        env = 'Development'
    elif 'madlb' in df_hosts['pop']:
        env = 'Preproduction'
    else:
        env = 'Production'

    inventory_string += '## InfraV {} inventory for Ansible\n'.format(env)
    inventory_string += '\n'

    inventory_string += '[{}:children]\n'.format(env[:3].lower())
    for key in pop_children_dict:
        inventory_string += '{}\n'.format(key[1:-1].split(':')[0])

    inventory_string += print_dict(pop_children_dict)
    inventory_string += print_dict(vendor_children_dict)
    inventory_string += print_dict(model_children_dict)

    # Dict unpacking
    #for key, value in children_dict.items():
    #    print('{}: {}'.format(key, value))

    ## One useful way to inspect a Pandas GroupBy object and see the splitting in action is to iterate over it. 
    ## This is implemented in DataFrameGroupBy.__iter__() and produces an iterator of (group, DataFrame) pairs for DataFrames
    for group, group_df in grp:
        print(group)
        # Writing PoP header and children groups
        if title != group[0]:
            title = group[0]
            inventory_string += '\n'
            inventory_string += '##\n'
            inventory_string += '## {}\n'.format(group[0].upper())
            inventory_string += '##\n'
            inventory_string += '\n'
            for key, value in children_dict.items():
                if group[0] in key:
                    inventory_string += '{}\n'.format(key)
                    for item in value:
                        inventory_string += '{}\n'.format(item)

        inventory_string += '\n'
        inventory_string += f'[{group[0]}_{group[1]}]'

        for i in range(len(group_df)):
            inventory_string += '\n'
            inventory_string += '{}   {}={}'.format(group_df['hostfqdn'].values[i], group_df['ipmivar'].values[i], group_df['ipmifqdn'].values[i])
        inventory_string += '\n'

    return inventory_string

def main():
    args = parse_arguments()
    vcenter_password = getpass.getpass(prompt='Enter vCenter password: ')
    si = connect(args.vcenter_ip, args.vcenter_user, vcenter_password)  # Connect to vCenter
    content = si.RetrieveContent()

    df_hosts = pd.DataFrame(columns=['hostfqdn', 'vendor', 'model', 'cluster', 'pop', 'ipmifqdn', 'ipmivar', 'ipmiip'])

    df_hosts = get_hosts_data(content, df_hosts)
    #print(df_hosts)

    inventory_string = build_group(df_hosts)
    print(inventory_string)

if __name__ == '__main__':
    main()
