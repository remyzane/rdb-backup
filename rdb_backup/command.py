import os
import sys
import click

from argparse import HelpFormatter, ArgumentParser

from rdb_backup.postgres import pg_tables
from rdb_backup.utility import get_config, tests_config


class CustomizeHelpFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        sys.stdout.write('%s%s%s' % (usage, os.linesep, os.linesep))

    def format_help(self):
        return None


def backup():
    dbs = get_config('postgres.yml', tests_config)
    for db in dbs:
        print(db.db_name)
        for table_name in pg_tables(db.db_name):
            print(table_name)


def restore():
    print('restore')


commands = locals()


def main():
    usage = [
        ' ------------------------------ help ------------------------------',
        ' -h                    show help message',
        ' backup                do backup',
        ' restore               do restore',
    ]
    parser = ArgumentParser(usage=os.linesep.join(usage), formatter_class=CustomizeHelpFormatter)
    parser.add_argument('command', type=str)
    parser.add_argument('-p', '--params', default=[])
    args = parser.parse_args()

    # run command
    if args.command not in ['backup', 'restore']:
        parser.print_help()
    else:
        commands[args.command](*[] if not args.params else args.params)
