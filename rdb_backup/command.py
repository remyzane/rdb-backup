import click

from rdb_backup.utility import get_config


def backup(config_file):
    dbs = get_config(config_file)
    for db in dbs:
        db.backup()


def restore(config_file):
    dbs = get_config(config_file)
    for db in dbs:
        db.restore()


@click.command()
@click.argument('command', type=click.Choice(['backup', 'restore']))
@click.argument('config_file')
def main(command, config_file):
    commands[command](config_file)

commands = locals()
