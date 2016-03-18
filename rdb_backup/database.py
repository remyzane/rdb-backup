
import os


class DatabaseProcessor(object):

    processor_name = None

    def __init__(self, db_name, config):
        self.db_name = db_name
        self.backup_root = config.pop('backup_root')
        self.backup_path = config.pop('backup_path')
        self.ignore = config.pop('ignore', None)
        self.define = config    # table define

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


class Mysql(DatabaseProcessor):

    processor_name = 'mysql'

    def __init__(self, db_name, config):
        self.username = config.pop('username')
        self.password = config.pop('password')
        super().__init__(db_name, config)       # super init must be on the back

    def backup(self):
        pass


class Postgres(DatabaseProcessor):

    processor_name = 'postgresql'

    pass


# generate in rdb_backup.utility.init_processor
database_processors = {}
