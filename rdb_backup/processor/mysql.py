import os
import logging

from rdb_backup.utility import run_shell
from rdb_backup.processor import DatabaseProcessor, TableProcessor

log = logging.getLogger(__name__)


class MysqlLocal(DatabaseProcessor):

    processor_name = 'mysql'

    tmp_dir = '/tmp/rdb_backup/mysql_local'
    if not os.path.exists(tmp_dir):
        run_shell('mkdir -p %s' % tmp_dir)
    run_shell('chmod og-rwx %s' % tmp_dir)

    def __init__(self, dbms, name, db_config, tb_config):
        super().__init__(dbms, name, db_config, tb_config)
        self.dump_sql = os.path.join(self.tmp_dir, '__%s__complete__.sql' % self.name)
        self.password = db_config.pop('password')
        self.username = db_config.pop('username')
        self.extended_insert = db_config.get('extended-insert', True)

    def run_mysql(self, sql):
        command = 'mysql -u %s -p\'%s\' -e "%s"' % (self.username, self.password, sql)
        return run_shell(command, cwd=self.tmp_dir)

    def table_names(self):
        process = self.run_mysql('use %s; show tables;' % self.name)
        out = process.stdout.readlines()
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables[1:]

    @staticmethod
    def write_schema_sql(schema_sql, line):
        if line.startswith('-- Dump completed on'):
            schema_sql.write('-- Dump completed')   # clear date time info
        else:
            schema_sql.write(line)

    def backup(self, need_backup_tables):
        dump_params = '-u %s -p\'%s\' --lock-all-tables --extended-insert=false' % (self.username, self.password)
        run_shell('mysqldump %s %s > %s' % (dump_params, self.name, self.dump_sql), cwd=self.tmp_dir)
        schema_sql = open(self.schema_sql, 'w')
        sign = 0
        table_sql = None
        insert_str = None
        insert_str_length = None
        fields = []
        for line in open(self.dump_sql):
            if sign == 0:
                if line.startswith('CREATE TABLE `'):
                    sign = 1
                    table_name = line[14:].split('`', 1)[0]
                    insert_str = 'INSERT INTO `%s` VALUES (' % table_name
                    insert_str_length = len(insert_str)
                    if table_name in need_backup_tables:
                        table_sql = need_backup_tables[table_name]
                self.write_schema_sql(schema_sql, line)
            elif sign == 1:
                if line.startswith('  `'):
                    fields.append(line[3:].split('`', 1)[0])
                else:
                    sign = 2
                    if table_sql:
                        table_sql.begin_backup(fields)
                self.write_schema_sql(schema_sql, line)
            elif sign == 2:
                if line.startswith('DROP TABLE IF EXISTS '):
                    sign = 0
                    if table_sql:
                        table_sql.close()
                    table_sql = None
                    insert_str = None
                    insert_str_length = None
                    fields = []
                    self.write_schema_sql(schema_sql, line)
                elif line.startswith(insert_str):
                    if table_sql:
                        table_sql.write_record(line[insert_str_length:-3])
                else:
                    self.write_schema_sql(schema_sql, line)

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
                if line.startswith('LOCK TABLES `'):
                    sign += 1
                    table_name = line[13:-9]
                import_sql.write(line)
                continue
            if sign == 1:
                import_sql.write(line)
                if self.ignored(table_name):
                    tables_ignored.append(table_name)
                else:
                    table_file_path = self.backup_path.replace('{table_name}', table_name)
                    if os.path.exists(table_file_path) and os.stat(table_file_path).st_size > 0:
                        if self.extended_insert:
                            split = ' '
                            import_sql.write('INSERT INTO `%s` VALUES' % table_name)
                            memory_size = 0
                            for data_line in open(table_file_path):
                                if memory_size > 1048576:   # 1024 * 1024
                                    import_sql.write(';' + os.linesep);
                                    import_sql.write('INSERT INTO `%s` VALUES' % table_name)
                                    memory_size = 0
                                    split = ' '
                                memory_size += len(data_line)
                                import_sql.write(split + '(' + data_line[:-1] + ')')
                                if split == ' ':
                                    split = ','
                            import_sql.write(';' + os.linesep);
                        else:
                            insert_sql = 'INSERT INTO `%s` VALUES (%%s);%s' % (table_name, '\n')
                            for data_line in open(table_file_path):
                                import_sql.write(insert_sql % data_line[:-1])
                sign = 0
                table_name = None
                continue
        if tables_ignored:
            log.info('ignored tables: %s' % tables_ignored)
        log.info('generate import file: %s', import_sql.name)
        import_sql.close()


class MysqlTable(TableProcessor):

    processor_name = 'mysql'

    def begin_backup(self, fields):
        self.set_field_names(fields)
        self.file = open(self.backup_path, 'w')

    @classmethod
    def get_record(cls, data):
        field = None
        in_mark = False
        in_wildcard = False
        fields = []
        for _char in data:
            if field is None:
                if _char == '\'':
                    in_mark = True
                    field = ''
                else:
                    in_mark = False
                    field = _char
            else:
                if in_mark:
                    if in_wildcard:
                        in_wildcard = False
                    else:
                        if _char == '\\':
                            in_wildcard = True
                        elif _char == '\'':
                            in_mark = False
                        else:
                            field += _char
                else:
                    if _char == ',':
                        fields.append(field)
                        field = None
                        in_mark = False
                    else:
                        field += _char
        fields.append(field)
        return fields

    def write_record(self, line):
        if self.filter is None:
            self.file.write(line + os.linesep)
        else:
            need_write = False
            field_name, operator, filter_value = self.filter
            record = self.get_record(line[:-len(os.linesep)])
            field_value = self.get_field(record, field_name)
            if operator == '>':
                if field_value > filter_value:
                    need_write = True
            if operator == '=':
                if filter_value == 'None':
                    if field_value == 'NULL':
                        need_write = True
                elif field_value == filter_value:
                    need_write = True
            if operator == '!=':
                if filter_value == 'None':
                    if field_value != 'NULL':
                        need_write = True
                elif field_value != filter_value:
                    need_write = True
            if operator == '<':
                if field_value < filter_value or field_value == 'NULL':      # or field_value is None
                    need_write = True
            if need_write:
                self.file.write(line + os.linesep)
