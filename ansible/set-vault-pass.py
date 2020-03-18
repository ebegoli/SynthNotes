#!/usr/bin/env python

import os

print("WARNING: This script prints your password to stdout. Use with caution!")

passwd = os.environ.get('ANSIBLE_VAULT_PASSWORD', None)

if passwd is None:
  raise Exception("Please set the environment variable ANSIBLE_VAULT_PASSWORD")

print(os.environ['ANSIBLE_VAULT_PASSWORD'])
