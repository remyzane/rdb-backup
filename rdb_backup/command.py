import os
import sys
import click

from rdb_backup.utility import get_config, run_shell


def backup(config_file):
    # get config
    communal_config, dbs = get_config(config_file)
    # chmod
    chmod = communal_config.get('chmod', 'u+rX,u-w,og-rwx')
    backup_root = communal_config['backup_root']
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)
    run_shell('chmod -R %s %s' % (chmod, backup_root))
    # do backup
    for db in dbs:
        db.backup()
    # chmod
    run_shell('chmod -R %s %s' % (chmod, backup_root))


def restore(config_file):
    communal_config, dbs = get_config(config_file)
    for db in dbs:
        db.restore()


def template(config_file):
    template_file = os.path.realpath(os.path.join(__file__, '..', 'template.yml'))
    run_shell('cp %s %s' % (template_file, config_file))
    run_shell('chmod og-rwx ' + config_file)
    sys.stdout.write('configure file [%s] generated.%s' % (config_file, os.linesep))


@click.command()
@click.argument('command', type=click.Choice(['backup', 'restore', 'template']))
@click.argument('config_file')
def main(command, config_file):
    commands[command](config_file)

commands = locals()
