# -*- coding: utf-8 -*-

"""
Usage: zooload.py -d <file with nodes dump> -s <server name> -p <port>
Restores dump of zookeeper nodes, created with zoodump.py script, on a custom host.
"""

import sys
import getopt
import logging
from kazoo.client import KazooClient, KazooState
import json


def main(argv):
    # dump_file is mandatory
    dump_file = None
    # host is mandatory
    host = None
    # default value for zookeeper port
    port = '2181'

    failed_nodes = []
    try:
        opts, args = getopt.getopt(argv, "hs:d:p:b:", ["server=", "dump=", "port=", "branch="])
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
        elif opt in ("-d", "--dump"):
            dump_file = arg

    if host is None:
        print("Parameter -s (--server) is mandatory. See --help for more information.")
        sys.exit(2)

    if dump_file is None:
        print("Parameter -d (--dump) is mandatory. See --help for more information.")
        sys.exit(2)

    logging.basicConfig()
    zk = KazooClient(hosts=host + ':' + port)
    zk.add_listener(zk_listener)
    try:
        with open(dump_file, 'r') as dump:
            nodes = json.loads(dump.read())
            print("{0} nodes read from dump file.".format(len(nodes)))
            zk.start()
            for node in nodes:
                try:
                    node_value = bytes(nodes[node], encoding='utf-8') if nodes[node] is not None else None
                    if not zk.exists(node):
                        zk.create(node, node_value, makepath=True)
                    else:
                        zk.set(node, node_value)
                except:
                    failed_nodes.append(node)
                    sys.__stderr__.write(
                        "Error when creating node {0}: {1} - {2}\n".format(node, sys.exc_info()[0], sys.exc_info()[1]))
            zk.stop()
            if len(failed_nodes) > 0:
                sys.__stderr__.write(
                    "Following nodes were not created on host {0} ({1} of {2}): {3}".format(host, len(failed_nodes),
                                                                                            len(nodes), failed_nodes))
                exit(1)
            else:
                print("{0} nodes were successfully created on host {1}".format(len(nodes), host))
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))


def zk_listener(state):
    if state == KazooState.LOST:
        print("Connection to zookeeper has been dropped.")
    elif state == KazooState.SUSPENDED:
        sys.stderr.write("Connection to zookeeper has been suspended.")
    elif state == KazooState.CONNECTED:
        print("Successfully connected to zookeeper host.")
    else:
        sys.stderr.write('Unexpected zookeeper connection state.')


def print_help():
    print("""zooload.py -d <file with nodes dump> -s <server name> -p <port>
              -d --dump     : dump file, created with zoodump.py script, mandatory argument
              -s --server   : zookeeper host, mandatory argument'
              -p --port     : zookeeper port, default = 2181'
             Example of usage: 
                zooload.py -d testsrv_zk_dump.json -s testsrv -p 2181""")


if __name__ == "__main__":
    main(sys.argv[1:])
