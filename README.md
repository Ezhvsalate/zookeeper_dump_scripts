# zookeeper_scripts

Sometimes you need to make a fast dump of zookeeper tree and store it on other host, for example when moving from one virtual machine to another.
Hope these small python scripts could help.

Tested on python 3.5, kazoo 2.2.1

## zoodump.py

Creates dump of zookeeper nodes in json format for further restoring it in another host.

Usage: 
```
zoodump.py -s <server name> -p <port> -b <start from branch> -e <exclude_branch1,exclude_branch2>

 -s --server   : zookeeper host, mandatory argument'
 -p --port     : zookeeper port, default = 2181'
 -b --branch   : root branch for reading, default behaviour is to read everything from root'
 -e --exclude  : comma-separated list of branches to exclude, default behaviour is not to exclude any branches
 ```
Example of usage:
``` 
zoodump.py -s testsrv -p 2181 -b /startbranch -e /branch/subbranch,/branch/not/export/me/please
```

## zooload.py

Restores dump of zookeeper nodes, created with zoodump.py script, on a custom host.

Usage: 
```
zooload.py -d <file with nodes dump> -s <server name> -p <port>'
  -d --dump     : dump file, created with zoodump.py script, mandatory argument'
  -s --server   : zookeeper host, mandatory argument'
  -z --port     : zookeeper port, default = 2181'
```
 Example of usage:
``` 
  zooload.py -d testsrv_zk_dump.json -s testsrv -p 2181
``` 
