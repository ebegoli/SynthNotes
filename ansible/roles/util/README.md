# util

The `util` role is used to hold generic helper tasks that may be included
by other roles.

## `keys.yml` 

Distributes SSH public keys from one group of hosts to another

## `download.yml`  

To automate download and verification of source code, we have written the generic
task `download.yml`. This task is delegated to `localhost`,
that is, the ansible controller, so that large files will be downloaded to the 
controller and distributed to the relevant hosts. We automatically verify
the checksum, specified as a global variable.

