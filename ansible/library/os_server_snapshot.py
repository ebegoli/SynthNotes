#!/usr/bin/python
# coding: utf-8 -*-

# Copyright (c) 2016, Mario Santos <mario.rf.santos@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


DOCUMENTATION = '''
---
module: os_volume_snapshot
short_description: Create/Delete Cinder Volume Snapshots
extends_documentation_fragment: openstack
version_added: "2.3"
author: "Mario Santos (@ruizink)"
description:
   - Create or Delete cinder block storage volume snapshots
options:
   server:
     description:
       - The server name or id from which to create/delete the snapshot
     required: True
   snapshot_name:
     description:
        - Name of the snapshot
     required: true
   display_description:
     description:
       - String describing the snapshot
     required: false
     default: None
   force:
     description:
       - Allows or disallows snapshot of a volume to be created when the volume
         is attached to an instance.
     required: false
     default: False
   state:
     description:
       - Should the resource be present or absent.
     choices: [present, absent]
     default: present
requirements:
     - "python >= 2.6"
     - "shade"
'''

EXAMPLES = '''
# Creates a snapshot on server 'test_server'
- name: create and delete snapshot
  hosts: localhost
  tasks:
  - name: create snapshot
    os_server_snapshot:
      state: present
      cloud: mordred
      availability_zone: az2
      snapshot_name: test_snapshot
      server: test_server
  - name: delete snapshot
    os_server_snapshot:
      state: absent
      cloud: mordred
      availability_zone: az2
      snapshot_name: test_snapshot
      server: test_server
'''

RETURN = '''
snapshot:
    description: The snapshot instance after the change
    returned: success
    type: dict
    sample:
      id: 837aca54-c0ee-47a2-bf9a-35e1b4fdac0c
      name: test_snapshot
      image_id: ec646a7c-6a35-4857-b38b-808105a24be6
      size: 2
      status: available
      snapshot_name: test_snapshot
'''

try:
    import shade

    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False


def _present_image_snapshot(module, cloud):
    server = cloud.get_server(module.params['server'])
    snapshot = cloud.get_image(module.params['snapshot_name'])
   
    if snapshot and module.params['force']:
        cloud.delete_image(name_or_id=snapshot.id,
                           wait=True,
                           timeout=module.params['timeout'],
                           )
        snapshot = cloud.get_image(module.params['snapshot_name'])
        if snapshot is not None:
            module.fail_json(
                msg="Error forcing rebuild of image snapshot '{}'".format(
                    module.params['snapshot_name']))

    if not snapshot:
        snapshot = cloud.create_image_snapshot(module.params['snapshot_name'],
                                               server.id,
                                               wait=module.params['wait'],
                                               timeout=module.params[
                                                   'timeout'],
                                               description=module.params.get(
                                                   'display_description')
                                               )
        module.exit_json(changed=True, snapshot=snapshot)
    else:
        module.exit_json(changed=False, snapshot=snapshot)


def _absent_image_snapshot(module, cloud):
    snapshot = cloud.get_image(module.params['snapshot_name'])
    
    if not snapshot:
        module.exit_json(changed=False)
    else:
        cloud.delete_image(name_or_id=snapshot.id,
                           wait=module.params['wait'],
                           timeout=module.params['timeout'],
                           )
        module.exit_json(changed=True, snapshot_id=snapshot.id)


def main():
    argument_spec = openstack_full_argument_spec(
        server=dict(required=True),
        snapshot_name=dict(required=True, aliases=['name']),
        display_description=dict(default=None, aliases=['description']),
        force=dict(required=False, default=False, type='bool'),
        state=dict(default='present', choices=['absent', 'present']),
    )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    state = module.params['state']

    try:
        cloud = shade.openstack_cloud(**module.params)
        if cloud.get_server(module.params['server']):
            if state == 'present':
                _present_image_snapshot(module, cloud)
            if state == 'absent':
                _absent_image_snapshot(module, cloud)
        else:
            module.fail_json(
                msg="No server with name or id '{}' was found.".format(
                    module.params['server']))
    except (shade.OpenStackCloudException, shade.OpenStackCloudTimeout) as e:
        module.fail_json(msg=e.message)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *

if __name__ == '__main__':
    main()
