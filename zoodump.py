# -*- coding: utf-8 -*-

"""
Usage: zoodump.py -s <server name> -p <port> -b <start from branch> -e <exclude_branch1,exclude_branch2>

Creates dump of zookeeper nodes in json format for further restoring it in another host.
Using -b parameter makes possible to start from custom branch.
Using -e parameter makes possible to exclude branches.
"""

import sys
import getopt
import logging
from kazoo.client import KazooClient, KazooState
import os
import json


def main(argv):
    # default value for zookeeper port
    port = '2181'
    # default behaviour is to read everything beginning from root
    branch = ''
    # default behaviour is not to exclude any branches
    exclude = ''
    # host is mandatory
    host = None

    result = {}
    try:
        opts, args = getopt.getopt(argv, "hs:p:b:e:", ["server=", "port=", "branch=", "exclude="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-s", "--server"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-b", "--branch"):
            branch = arg
        elif opt in ("-e", "--exclude"):
            exclude = arg.split(',')

    if host is None:
        print('Parameter -s (--server) is mandatory. See --help for more information.')
        sys.exit(2)

    logging.basicConfig()
    zk = KazooClient(hosts=host + ':' + port, read_only=True)
    zk.add_listener(zk_listener)
    zk.start()
    get_nodes(zk, branch, result, exclude)
    zk.stop()

    with open(host + "_zk_dump.json", "w") as f:
        f.write(json.dumps(result, sort_keys=True, indent=4,
                           separators=(',', ': ')))

    print("{0} nodes succesfully stored in file {1}{2}{3}_zk_dump.json".format(len(result), os.getcwd(), os.sep, host))


def zk_listener(state):
    if state == KazooState.LOST:
        print("Connection to zookeeper has been dropped.")
    elif state == KazooState.SUSPENDED:
        sys.stderr.write('Connection to zookeeper has been suspended.')
    elif state == KazooState.CONNECTED:
        print("Successfully connected to zookeeper host.")
    else:
        sys.stderr.write('Unexpected zookeeper connection state.')


def print_help():
    print("""zoodump.py -s <server name> -p <port> -b <start from branch> -e <exclude_branch1,exclude_branch2>
           -s --server   : zookeeper host, mandatory argument
           -p --port     : zookeeper port, default = 2181
           -b --branch   : root branch for reading, default behaviour is to read everything from root
           -e --exclude  : comma-separated list of branches to exclude, default behaviour is not to exclude branches
          Example of usage: 
          zoodump.py -s testsrv -p 2181 -b /startbranch -e /branch/subbranch,/branch/not/export/me/please""")


def get_nodes(zk, path, dic, exclude):
    children = zk.get_children(path=path)
    for child in children:
        child_path = path + "/" + child
        if child_path not in exclude:
            data, stat = zk.get(child_path)
            if data is not None:
                dic[child_path] = data.decode("utf-8")
            else:
                dic[child_path] = None
            if stat.numChildren > 0:
                get_nodes(zk, child_path, dic, exclude)


if __name__ == "__main__":
    main(sys.argv[1:])
