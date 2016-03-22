import os

from rdb_backup.table import table_processors
from rdb_backup.utility import ProcessorNonexistent


class DatabaseProcessor(object):

    processor_name = None

    def __init__(self, db_name, db_config, tb_config):
        self.db_name = db_name
        self.backup_root = db_config.pop('backup_root')
        self.backup_path = db_config.pop('backup_path')
        self.ignore_list = db_config.pop('ignore', '').split()
        self.define = {}    # table define
        for tb_name, define in tb_config.items():
            table_processor = 'default'
            selector = None
            params = None
            if type(define) == str:
                selector = define
            elif type(define) == dict:
                selector = define.pop('selector', None)
                table_processor = define.pop('processor', 'default')
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

    def get_path(self, table_name, section_name=None):
        self.config['backup_path'] = self.config['backup_path'].replace('{date_time}', '2222222')
        if section_name:
            return os.path.join(self.config['backup_path'], table_name, section_name)
        else:
            return os.path.join(self.config['backup_path'], table_name)

    def backup(self):
        for table in self.tables_need_process():
            print(table)

    def restore(self):
        for table in self.tables_need_process():
            print(table)

    def tables_need_process(self):
        tables = []
        for table_name in self.tables_all():
            if not self.__ignored(table_name):
                tables.append(table_name)
        return tables

    # implement in subclass
    def tables_all(self):
        raise NotImplementedError

# generate in rdb_backup.utility.init_processor
database_processors = {}
