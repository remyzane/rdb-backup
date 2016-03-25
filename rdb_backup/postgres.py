import os

from rdb_backup.utility import run_shell
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor

PG_TABLES_SQL = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"


def run_psql(db, sql, cwd='/tmp'):
    command = 'psql %s -c "%s"' % (db, sql)
    return run_shell(command, 'postgres', cwd)


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgres'

    def tables_all(self):
        process = run_psql(self.name, PG_TABLES_SQL)
        out = process.stdout.readlines()
        out = out[2:-2]
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables

    def backup_schema(self, schema_path):
        tmp_path = '/tmp/__%s__schema__.sql' % self.name
        run_shell('pg_dump --schema-only %s > %s' % (self.name, tmp_path), 'postgres')
        run_shell('mv %s %s' % (tmp_path, schema_path))


class PostgresTable(TableProcessor):

    processor_name = 'postgres'

    def backup(self):
        dir_path = os.path.dirname(self.backup_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        print(self.backup_path)
        pass

    def restore(self):
        pass
