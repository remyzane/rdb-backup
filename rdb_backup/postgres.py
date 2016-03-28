import os
import logging

from rdb_backup.utility import run_shell
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor

QUERY_TABLES_SQL = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
log = logging.getLogger(__name__)


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgres'

    tmp_dir = '/tmp/rdb_backup_postgres_local'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    run_shell('chown postgres:postgres %s' % tmp_dir)
    run_shell('chmod og-rwx %s' % tmp_dir)

    @classmethod
    def run_psql(cls, db, sql):
        command = 'psql %s -c "%s"' % (db, sql)
        return run_shell(command, 'postgres', cwd=cls.tmp_dir)

    def tables_all(self):
        process = self.run_psql(self.name, QUERY_TABLES_SQL)
        out = process.stdout.readlines()
        out = out[2:-2]
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables

    def backup_schema_and_tables(self, need_backup_tables):
        complete_sql = os.path.join(self.tmp_dir, '__%s__complete__.sql' % self.name)
        log.info('dumping ...')
        run_shell('pg_dump %s > %s' % (self.name, complete_sql), 'postgres', cwd=self.tmp_dir)
        schema_sql = open(self.schema_sql, 'w')
        sign = 0
        table_sql = None
        for line in open(complete_sql):
            if sign == 0:
                if line.startswith('-- Data for Name: '):
                    sign = 1
                    table_name = line.split(';')[0].split()[-1]
                    if table_name in need_backup_tables:
                        table_sql_path = need_backup_tables[table_name].backup_path
                        log.info('backup ' + table_sql_path)
                        table_sql = open(table_sql_path, 'w')
                schema_sql.write(line)
                continue
            if sign == 1:       # write '--' line
                sign = 2
                schema_sql.write(line)
                continue
            if sign == 2:
                if table_sql:
                    table_sql.write(line)
                if line == '\.' + os.linesep:
                    sign = 0
                    table_sql = None
                continue

        log.info('backup ' + self.schema_sql)
        os.unlink(complete_sql)


class PostgresTable(TableProcessor):

    processor_name = 'postgres'

    def backup(self):

        # run_shell('pg_dump -t %s %s > %s' % (self.name, self.db.name, tmp_path), 'postgres', cwd=self.db.tmp_dir)
        # run_shell('mv %s %s' % (tmp_path, self.backup_path))
        # run_shell('chown root:root %s' % self.backup_path)

        print(self.backup_path)
        pass

    def restore(self):
        pass
