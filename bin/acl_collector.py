#! /usr/bin/env python3
"""Connect to Cisco and Juniper Devices, retrieve an ACL and store in a database"""
from __future__ import print_function
from pathlib import Path
import os
import yaml
from pprint import pprint
import dbfunctions as db
import sys
import inventory
from netmiko import ConnectHandler
import re
import errno

CONFIG_DIR = '/path/to/acl-reports/config/'
CREDENTIALS = '/path/to/acl-reports/config/.CREDENTIALS.yml'
BIN_DIR = '/path/to/acl-reports/bin/'
INVENTORY = '/path/to/acl-reports/config/inventory.py'


def main():
    """The main function"""
    does_file_exist(BIN_DIR, INVENTORY)
    does_file_exist(CONFIG_DIR, CREDENTIALS)
    credential_file_permissions(CONFIG_DIR, CREDENTIALS)
    """details is a dictionary of the following values from the acl_details table
    acl_id     : An auto incremental value to uniquely identify the correct record
    customer_id: Linked to the customer_id in the customers tables
    acl_name   : The name of the ACL as configured on the router
    acl_format : Whether it's Cisco or Juniper as they have different output
    router     : The router it's configured on. Required for connection parameters
    """
    for details in db.get_acl_details_for_db():
        if details['acl_format'] == 'cisco':
            #print('Cisco is on holiday')
            cisco_acl(details['customer_id'], details['acl_name'], details['router'])
        elif details['acl_format'] == 'junos':
            #print(db.create_juniper_matches_table(details['acl_name']))
            juniper_acl(details['customer_id'], details['acl_id'], details['acl_name'], 
                        details['router'])
            #print('Juniper is on holiday')
        else:
            print('undefined')


def does_file_exist(directory, filename):
    """Checking that a file exists"""
    path_to_file = Path(directory + filename)
    try:
        check_file = path_to_file.resolve()
    except FileNotFoundError:
        print(filename + " does not exist")
    else:
        return True


def credential_file_permissions(directory, filename):
    """Is the CREDENTIALS file world readable? It should not be"""
    perms = '0600'
    cred_file = directory + filename
    st = os.stat(cred_file)
    oct_perms = oct(st.st_mode)[-4:]
    if int(oct_perms) != int(perms):
        sys.exit(cred_file + " does not have the correct permissions. Change to 600")
    else:
        return True

def format_router_name(router):
    """ We need to remove the final 9 characters because this is the fqdn and is 
    not needed here, just the hostname. Also, the fqdn has dots and hyphen which python
    will interpret as the subtraction operator and the class attribute dot."""
    rtr = router[:-9]
    nice_name = rtr.replace('-', r'_').replace('.', r'_')
    return nice_name


def connection_parameters(router):
    """Let's build the connection details!"""
    hostname = format_router_name(router)
    params = getattr(INVENTORY, hostname)
    with open(CONFIG_DIR + CREDENTIALS) as c:
        try:
            creds = yaml.load(c)
            params['username'] = creds[0]['username']
            params['password'] = creds[0]['password']
            params['secret'] = creds[0]['secret']
        except yaml.YAMLError as e:
            print(e)
  
        return params


def cisco_acl(customer_id, acl_name, router):
    """Get the cisco acl"""
    device = connection_parameters(router)
    show_acl = 'show ip access-list ' + acl_name
  
    router_connection = ConnectHandler(**device)
    acl_output = router_connection.send_command(show_acl)
    router_connection.disconnect()
    parse_cisco_acl(customer_id, acl_name, acl_output, router)


def juniper_acl(customer_id, acl_id, acl_name, router):
    """Get the Juniper ACL"""
    device = connection_parameters(router)
    show_acl = 'show configuration firewall family inet filter ' + acl_name + ' | display set'
    show_matches = 'show firewall filter ' + acl_name
  
    router_connection = ConnectHandler(**device)
    acl_output = router_connection.send_command(show_acl)
    matches_output = router_connection.send_command(show_matches)
    router_connection.disconnect()
    parse_juniper_acl(customer_id, router, acl_name, acl_output)
    parse_juniper_matches(customer_id, router, acl_id, acl_name, matches_output)


def parse_cisco_acl(customer_id, acl_name, output, router):
    """Parse the ACL into three parts """
    table_name = acl_name+'_'+format_router_name(router)

    if db.does_table_exist(table_name) is None:
        db.create_cisco_table(table_name)

    lines = output.splitlines()
    for line in lines[1:]:
        l = line.lstrip()
        #split the line into two parts, the sequence number and everything else
        parts = l.split(' ', 1)
        m = re.search(r"\(([a-z 0-9]+)\)", parts[1])
        if m:
            sequence = parts[0]
            statement = re.sub(r"\(([a-z 0-9]+)\)", '', parts[1])
            matches = re.sub(r"([a-z]+)", '', m.group(1))
        else:
            sequence = parts[0]
            statement = parts[1]
            matches = ''
        db.insert_cisco_acl(table_name, customer_id, sequence, statement, matches)


def parse_juniper_acl(customer_id, router, acl_name, acl_output):
    """Parse the Juniper ACL"""
    table_name = acl_name+'_'+format_router_name(router)  

    if db.does_table_exist(table_name) is None:
        db.create_juniper_table(table_name)
    lines = acl_output.splitlines()
    for line in lines[1:]:
        if line is not None:
            db.insert_juniper_acl(table_name, customer_id, line)


def parse_juniper_matches(customer_id, router, acl_id, acl_name, match_output):
    """Why does Juniper have to put this in different output?"""
    table_name = acl_name+'_'+format_router_name(router)+'_matches'
    if db.does_table_exist(table_name) is None:
        db.create_juniper_matches_table(table_name)

    lines = match_output.splitlines()
    for line in lines[3:]:
        if line is not None:
            l = ' '.join(line.split())
            match = l.split()
        if length_of_list(match) > int(1):
            if match[1].isdigit():
                term = match[0]
                byte_count = match[1]
                packets = match[2]
                db.insert_juniper_matches(table_name, acl_id, customer_id, term, packets)


def length_of_list(match):
    """How long is the fucking list?"""
    length = len(match)
    return length

def is_int(element):
    """Is it a fucking integer?"""
    if element.isdigit():
        return True


"""Do Not Edit below this line"""
if __name__ == '__main__':
    main()
