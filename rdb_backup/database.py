
import os


class DatabaseProcessor(object):

    def __init__(self, db_name, config):
        self.db_name = db_name
        self.config = config

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

    name = 'mysql'

    def backup(self):
        pass


class Postgres(DatabaseProcessor):

    name = 'postgresql'

    pass


# generate in rdb_backup.utility.init_processor
database_classes = {}
