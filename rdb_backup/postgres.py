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

    def table_names(self):
        process = self.run_psql(self.name, QUERY_TABLES_SQL)
        out = process.stdout.readlines()
        out = out[2:-2]
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables

    def dump_data(self, need_backup_tables):
        complete_sql = os.path.join(self.tmp_dir, '__%s__complete__.sql' % self.name)
        log.info('dumping ...')
        run_shell('pg_dump %s > %s' % (self.name, complete_sql), 'postgres', cwd=self.tmp_dir)
        schema_sql = open(self.schema_sql, 'w')
        sign = 0
        table_sql = None
        for line in open(complete_sql):
            if sign == 0:
                if line.startswith('-- Data for Name: '):
                    sign += 1
                schema_sql.write(line)
                continue
            if sign in [1, 2]:      # '--' and space line
                sign += 1
                schema_sql.write(line)
                continue
            if sign == 3:           # field names
                sign += 1
                table_name = line.split()[1]
                if table_name in need_backup_tables:
                    table_sql = need_backup_tables[table_name]
                    table_sql.write_header(line)
                continue
            if sign == 4:
                if line == '\.' + os.linesep:
                    sign = 0
                    if table_sql:
                        table_sql.write_other(line)
                        table_sql.file.close()
                        table_sql = None
                else:
                    if table_sql:
                        table_sql.write_record(line)
                continue

        log.info('backup ' + self.schema_sql)
        os.unlink(complete_sql)


class PostgresTable(TableProcessor):

    processor_name = 'postgres'

    def write_header(self, line):
        log.info('backup ' + self.backup_path)
        self.file = open(self.backup_path, 'w')
        self.set_field_names(line.split('(')[1].split(')')[0].split(', '))
        self.file.write(line)

    def write_record(self, line):
        if self.filter is None:
            self.file.write(line)
        else:
            need_write = False
            field_name, operator, filter_value = self.filter
            record = line[:-len(os.linesep)].split('\t')
            field_value = self.get_field(record, field_name)
            print(field_value)
            if operator == '>':
                if field_value > filter_value:
                    need_write = True
            if operator == '=':
                if field_value == filter_value:
                    need_write = True
            if operator == '<':
                if field_value < filter_value:
                    need_write = True
            if need_write:
                print('---', line[:19])
                self.file.write(line)

    def write_other(self, line):
        self.file.write(line)

    def restore(self):
        pass
