# roles

Roles have been grouped by software, essentially. Please factor the role
tasks into `common.yml`, `conf.yml`, and executables. Common installs the 
software in standard location `{{ deploy_dir }}`, conventionally `/opt`.
The software should write logs, pids, etc to `{{ write_dir }}`. For tarballs
that simply need to be extracted, the `util` role has the generic task 
`standard-install.yml`, which should be used for this purpose. 
See `hbase/tasks/common` for example.

## Source files

Source files should not be commited to the repository. The `standard-install`
script will try to download the source from an ftp server at `172.22.4.129` to
the ansible controller (i.e.`localhost`) if it is not already present. 
The `<role>/files` directory needs to be present for this to work correctly,
so best practice is to commit `<role>/files/.gitgnore` to the repo.
