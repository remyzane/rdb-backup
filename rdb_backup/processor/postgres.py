import os
import logging

from rdb_backup.utility import run_shell
from rdb_backup.processor import DatabaseProcessor, TableProcessor

QUERY_TABLES_SQL = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
log = logging.getLogger(__name__)


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgres'

    tmp_dir = '/tmp/rdb_backup/postgres_local'
    if not os.path.exists(tmp_dir):
        run_shell('mkdir -p %s' % tmp_dir)
    run_shell('chown postgres:postgres %s' % tmp_dir)
    run_shell('chmod og-rwx %s' % tmp_dir)

    def __init__(self, dbms, name, db_config, tb_config):
        DatabaseProcessor.__init__(self, dbms, name, db_config, tb_config)
        self.dump_sql = os.path.join(self.tmp_dir, '__%s__complete__.sql' % self.name)

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

    def backup(self, need_backup_tables):
        run_shell('pg_dump %s > %s' % (self.name, self.dump_sql), 'postgres', cwd=self.tmp_dir)
        schema_sql = open(self.schema_sql, 'w')
        sign = 0
        table_sql = None
        for line in open(self.dump_sql):
            if sign == 0:
                if line.startswith('-- Data for Name: '):
                    sign += 1
                schema_sql.write(line)
            elif sign in [1, 2]:      # '--' and space line
                sign += 1
                schema_sql.write(line)
            elif sign == 3:           # field names
                sign += 1
                table_name = line.split()[1].replace('"', '')
                if table_name in need_backup_tables:
                    table_sql = need_backup_tables[table_name]
                    table_sql.write_header(line)
            elif sign == 4:
                if line == '\.' + os.linesep:
                    sign = 0
                    if table_sql:
                        table_sql.write_other(line)
                        table_sql.file.close()
                        table_sql = None
                else:
                    if table_sql:
                        table_sql.write_record(line)

        log.info('backup ' + self.schema_sql)
        if not self.debug:
            os.unlink(self.dump_sql)

    def restore(self):
        tables_ignored = []
        import_sql = open(self.backup_path.replace('{table_name}', 'import'), 'w')
        sign = 0
        table_name = None
        for line in open(self.schema_sql):
            if sign == 0:
                if line.startswith('-- Data for Name: '):
                    sign += 1
                    table_name = line[18:].split(';', 1)[0]
                import_sql.write(line)
                continue
            if sign == 1:      # '--'
                sign += 1
                import_sql.write(line)
                continue
            if sign == 2:      # space line
                import_sql.write(line)
                if self.ignored(table_name):
                    tables_ignored.append(table_name)
                else:
                    for data_line in open(self.backup_path.replace('{table_name}', table_name)):
                        import_sql.write(data_line)
                sign = 0
                table_name = None
                continue
        if tables_ignored:
            log.info('ignored tables: %s' % tables_ignored)
        log.info('generate import file: %s', import_sql.name)
        import_sql.close()


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
            if operator == '>':
                if field_value > filter_value:
                    need_write = True
            if operator == '=':
                if filter_value == 'None':
                    if field_value == '\\N':
                        need_write = True
                elif field_value == filter_value:
                    need_write = True
            if operator == '!=':
                if filter_value == 'None':
                    if field_value != '\\N':
                        need_write = True
                elif field_value != filter_value:
                    need_write = True
            if operator == '<':
                if field_value < filter_value or field_value == '\\N':      # or field_value is None
                    need_write = True
            if need_write:
                self.file.write(line)

    def write_other(self, line):
        self.file.write(line)
