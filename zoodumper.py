import json
import os
import sys

import click
from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import KazooException


@click.group()
def cli():
    pass


def zk_listener(state):
    if state == KazooState.LOST:
        click.echo("Connection to zookeeper has been dropped.")
    elif state == KazooState.SUSPENDED:
        click.echo(click.style('Connection to zookeeper has been suspended.', fg='red'))
    elif state == KazooState.CONNECTED:
        click.echo(click.style("Successfully connected to zookeeper host.", fg='green'))
    else:
        click.echo(click.style('Unexpected zookeeper connection state.', fg='red'))


@click.command()
@click.option('-s', '--server', type=str, required=True, help='zookeeper host')
@click.option('-p', '--port', type=int, default='2181', help='zookeeper port, by default it is 2181')
@click.option('-b', '--branch', type=str, default='', help='root branch for reading, default behaviour is to read everything from root')
@click.option('-e', '--exclude', type=str, default='', help='comma-separated list of branches to exclude, default behaviour is not to exclude branches')
def dump(server, port, branch, exclude):
    """Dumps zookeeper nodes and their values to json file."""

    def get_nodes(zk, path, dic, exclude):
        children = zk.get_children(path=path)
        click.echo(f"Current node: {path}")
        for child in children:
            child_path = path + "/" + child
            if child_path not in exclude:
                data, stat = zk.get(child_path)
                dic[child_path] = data.decode('utf-8') if data is not None else None
                if stat.numChildren > 0:
                    get_nodes(zk, child_path, dic, exclude)

    result = {}
    zk = KazooClient(hosts=f"{server}:{port}", read_only=True)
    zk.add_listener(zk_listener)
    zk.start()
    get_nodes(zk, branch, result, exclude)
    zk.stop()
    with open(f"{server}.zk.json", "w") as f:
        f.write(json.dumps(result, sort_keys=True, indent=4,
                           separators=(',', ': ')))
    click.echo(click.style(f"{len(result)} nodes succesfully stored in file {os.getcwd()}{os.sep}{server}.zk.json", fg='green'))


@click.command()
@click.option('-s', '--server', type=str, required=True, help='zookeeper host')
@click.option('-p', '--port', type=int, default='2181', help='zookeeper port, by default it is 2181')
@click.option('-f', '--dump_file', type=str, required=True, help='dump file, created when executed dump command')
def load(server, port, dump_file):
    """Loads zookeeper nodes and their values from dump file. If node exists - it's value will be updated, if doesn't exist - will be created."""
    failed_nodes = []
    zk = KazooClient(hosts=f"{server}:{port}")
    zk.add_listener(zk_listener)
    try:
        with open(dump_file, 'r') as dump:
            nodes = json.loads(dump.read())
            click.echo(click.style(f"{len(nodes)} nodes read from dump file.", fg='green'))
            zk.start()
            for node in nodes:
                try:
                    node_value = bytes(nodes[node], encoding='utf-8') if nodes[node] is not None else None
                    if not zk.exists(node):
                        click.echo(f"Creating node: {node}")
                        zk.create(node, node_value, makepath=True)
                    else:
                        click.echo(f"Updating value of node: {node}")
                        zk.set(node, node_value)
                except KazooException:
                    failed_nodes.append(node)
                    click.echo(click.style(f"Error when creating node {node}: {sys.exc_info()[0]} - {sys.exc_info()[1]}", fg='red'))
            zk.stop()
            if len(failed_nodes) > 0:
                click.echo(click.style(f"Following nodes were not created on host {server} ({len(failed_nodes)} of {len(nodes)}): {failed_nodes}", fg='red'))
                exit(1)
            else:
                click.echo(click.style(f"{len(nodes)} nodes were successfully created on host {server}", fg='green'))
    except IOError as e:
        click.echo(click.style(f"I/O error({e.errno}): {e.strerror}", fg='red'))


cli.add_command(dump)
cli.add_command(load)
