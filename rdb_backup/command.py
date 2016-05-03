import os
import sys
import click
import logging

from rdb_backup.utility import get_config, run_shell

log = logging.getLogger(__name__)


def backup(config_file, database=None):
    communal_config, dbs = get_config(config_file)
    log.info('backup %s%s', os.path.join(os.getcwd(), config_file), ' --db ' + database if database else '')

    mode = communal_config.get('chmod', 'u+rX,u-w,og-rwx')
    backup_root = communal_config['backup_root']
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)
        run_shell('chmod -R %s %s' % (mode, backup_root))

    changed = False
    for db in dbs:
        if database is None or db.name == database:
            log.info('------------------------ backup %s -----------------------' % db.name)
            db.backup(db.tables_need_backup())
            log.info('%s--------------------------------------------------------' % ('-' * len(db.name)))
            changed = True
    if not changed:
        log.info('nothing todo')
    else:
        run_shell('chmod -R %s %s' % (mode, backup_root))


def restore(config_file, database=None):
    communal_config, dbs = get_config(config_file)
    log.info('restore %s%s', os.path.join(os.getcwd(), config_file), ' --db ' + database if database else '')

    changed = False
    for db in dbs:
        if database is None or db.name == database:
            log.info('------------------------ restore %s -----------------------' % db.name)
            db.restore()
            log.info('%s---------------------------------------------------------' % ('-' * len(db.name)))
            changed = True
    if not changed:
        log.info('nothing todo')


def template(config_file):
    template_file = os.path.realpath(os.path.join(__file__, '..', 'template.yml'))
    run_shell('cp %s %s' % (template_file, config_file))
    run_shell('chmod og-rwx ' + config_file)
    sys.stdout.write('configure file [%s] generated.%s' % (config_file, os.linesep))


@click.command()
@click.argument('command', type=click.Choice(['backup', 'restore', 'template']))
@click.argument('config_file')
@click.option('--db')
def main(command, config_file, db):
    commands[command](config_file, db)

commands = locals()
