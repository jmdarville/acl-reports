#!/usr/bin/env python3

"""As the netmiko library requires parameters to be passed as a dictionary,
it's easier to simply hold the minimum values in a dictionary. I just can't be
bothered parsing yaml into a working solution.
Usernames and passwords are read from a hidden credentials file that should be
readable only to the user.
"""

cisco_xe_host = {
  'device_type': 'cisco_xe',
  'host' : 'hostname',
  'port': '22',
  'verbose': False
}

juniper_host = {
  'device_type': 'juniper',
  'host' : 'hostname',
  'port': '22',
  'verbose': False
}

