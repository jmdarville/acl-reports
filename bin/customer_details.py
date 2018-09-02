#!/usr/bin/env python3
#!-*- coding: utf-8 -*-
import dbfunctions as db
from pprint import pprint

acls = db.get_acls()
for acl in acls:
  if acl['acl_format'] == 'cisco':
    print("Cisco Format", acl['acl_name'])
  elif acl['acl_format'] == 'junos':
    print('You ate my Juniper berries...', acl['acl_name'])
