import os
import logging
from datetime import datetime

from rdb_backup.table import table_processors
from rdb_backup.utility import ProcessorNonexistent, run_shell

log = logging.getLogger(__name__)


class DatabaseProcessor(object):

    processor_name = None

    def __init__(self, dbms, name, db_config, tb_config):
        self.dbms = dbms
        self.name = name
        self.backup_root = db_config.pop('backup_root')
        self.backup_path = self.__get_path(db_config.pop('backup_path'))
        self.ignore_list = db_config.pop('ignore', '').split()
        self.define = {}    # table define
        for tb_name, define in tb_config.items():
            table_processor = self.processor_name
            selector = None
            params = None
            if type(define) == str:
                selector = define
            elif type(define) == dict:
                selector = define.pop('selector', None)
                table_processor = define.pop('processor', self.processor_name)
                params = define

            processor_class = table_processors.get(table_processor)
            if not processor_class:
                raise ProcessorNonexistent('table processor [%s] nonexistent.' % table_processor)

            self.define[tb_name] = processor_class(self, tb_name, params, selector)

    def __ignored(self, name):
        for item in self.ignore_list:
            if item[-1] == '*':
                if name.startswith(item[:-1]):
                    return True
                else:
                    return False
            elif item == name:
                return True
        return False

    def __get_path(self, backup_path):
        backup_path = backup_path.replace('{dbms_name}', self.dbms)
        backup_path = backup_path.replace('{db_name}', self.name)
        backup_path = backup_path.replace('{date_time}', datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        return os.path.join(self.backup_root, backup_path)

    def backup(self):
        log.info('backup database [%s] ----------------------------------------' % self.name)
        db_path = self.backup_path.split('{table_name}')[0]
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        schema_sql_path = os.path.join(db_path, '__structure__.sql')
        self.backup_schema(schema_sql_path)

        for table in self.tables_need_process():
            table.backup()
        log.info('------------------------------ database [%s] backup completed' % self.name)

    def restore(self):
        for table in self.tables_need_process():
            table.restore()

    def tables_need_process(self):
        tables = []
        tables_ignored = []
        for table_name in self.tables_all():
            if self.__ignored(table_name):
                tables_ignored.append(table_name)
            else:
                if table_name in self.define:
                    tables.append(self.define[table_name])
                else:
                    tables.append(table_processors[self.processor_name](self, table_name, {}))
        if tables_ignored:
            log.info('ignored tables: %s' % tables_ignored)
        return tables

    # implement in subclass
    def tables_all(self):
        raise NotImplementedError

    # implement in subclass
    def backup_schema(self, schema_path):
        raise NotImplementedError

# generate in rdb_backup.utility.init_processor
database_processors = {}
