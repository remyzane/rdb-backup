
import os

from rdb_backup.table import table_processors
from rdb_backup.utility import ProcessorNonexistent


class DatabaseProcessor(object):

    processor_name = None

    def __init__(self, db_name, db_config, tb_config):
        self.db_name = db_name
        self.backup_root = db_config.pop('backup_root')
        self.backup_path = db_config.pop('backup_path')
        self.ignore = db_config.pop('ignore', None)
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

    def get_path(self, table_name, section_name=None):
        self.config['backup_path'] = self.config['backup_path'].replace('{date_time}', '2222222')
        if section_name:
            return os.path.join(self.config['backup_path'], table_name, section_name)
        else:
            return os.path.join(self.config['backup_path'], table_name)

    def backup(self):
        pass

    def restore(self):
        pass


class MysqlLocal(DatabaseProcessor):

    processor_name = 'mysql'

    def __init__(self, db_name, db_config, tb_config):
        super().__init__(db_name, db_config, tb_config)
        self.username = db_config.pop('username')
        self.password = db_config.pop('password')

    def backup(self):
        pass


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgresql'

    pass


# generate in rdb_backup.utility.init_processor
database_processors = {}
