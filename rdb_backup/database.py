import os
import logging
from datetime import datetime

from rdb_backup.table import table_processors
from rdb_backup.utility import ProcessorNonexistent

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

        db_path = self.backup_path.split('{table_name}')[0]
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.schema_sql = os.path.join(db_path, '__schema__.sql')

        for tb_name, define in tb_config.items():
            table_processor = self.processor_name
            params = None
            if type(define) == dict:
                table_processor = define.pop('processor', self.processor_name)
                params = define

            processor_class = table_processors.get(table_processor)
            if not processor_class:
                raise ProcessorNonexistent('table processor [%s] nonexistent.' % table_processor)

            self.define[tb_name] = processor_class(self, tb_name, params)

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
        log.info('------------------------ backup %s ----------------------->' % self.name)
        self.dump_data(self.tables_need_process())
        log.info('------------------ %s backup completed -------------------<' % self.name)

    def restore(self):
        for table in self.tables_need_process().values():
            table.restore()

    def tables_need_process(self):
        tables = {}
        tables_ignored = []
        table_names = self.table_names()
        for table_name in self.define.keys():
            if table_name not in table_names:
                raise IndexError('defined table [%s] is not exists in database [%s]' % (table_name, self.name))

        for table_name in table_names:
            if self.__ignored(table_name):
                tables_ignored.append(table_name)
            else:
                if table_name in self.define:
                    tables[table_name] = self.define[table_name]
                else:
                    tables[table_name] = table_processors[self.processor_name](self, table_name, {})
        if tables_ignored:
            log.info('ignored tables: %s' % tables_ignored)
        return tables

    # implement in subclass
    def table_names(self):
        raise NotImplementedError

    # implement in subclass
    def dump_data(self, need_backup_tables):
        raise NotImplementedError

# generate in rdb_backup.utility.init_processor
database_processors = {}
