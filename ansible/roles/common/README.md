# common

The common role sets configurations that are common to every node in the cluster.
One of the chief tasks in the common role is to populate the `/etc/hosts` file
for each node to include a host name and IP address for every other node in the
cluster, which enables reverse-DNS lookup.

Another task is to `yum` install basic CentOS dependencies.

Java is also installed via `yum`, but additionally, the `JAVA_HOME` environment
variable is set through the file `/etc/profile.d/java.sh`. The development
version of OpenJDK is installed in order to use the diagnostic tools such as 
'jps'.
