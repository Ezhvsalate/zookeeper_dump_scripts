# zoodumper

Sometimes you need to make a fast dump of zookeeper tree and store it on other host, for example when moving from one virtual machine to another.
Hope these small utility could help.

Tested on python 3.6, kazoo 2.2.1

## Installation:

A tool can be easily installed using pip:
``` 
pip install zoodumper
```

## Dump data from zookeeper

zoodumper dump [OPTIONS]

  Dumps zookeeper nodes and their values to json file.

Options:
  -s, --server TEXT   zookeeper host  [required]
  -p, --port INTEGER  zookeeper port, by default it is 2181
  -b, --branch TEXT   root branch for reading, default behaviour is to read everything from root
  -e, --exclude TEXT  comma-separated list of branches to exclude, default behaviour is not to exclude branches

 Example of usage:
``` 
zoodumper dump -s testsrv -p 2181 -b /startbranch -e /branch/subbranch,/branch/not/export/me/please
```

## Load data from dump to zookeeper

zoodumper load [OPTIONS]

  Loads zookeeper nodes and their values from dump file. If node exists -
  it's value will be updated, if doesn't exist - will be created.

Usage: 
Options:

  -s, --server TEXT     zookeeper host  [required]  
  -p, --port INTEGER    zookeeper port, by default it is 2181  
  -f, --dump_file TEXT  dump file, created when executed dump command [required]

Example of usage:
``` 
zoodumper load -f testsrv.zk.json -s testsrv -p 2181
```
