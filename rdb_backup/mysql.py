from rdb_backup.database import DatabaseProcessor


class MysqlLocal(DatabaseProcessor):

    processor_name = 'mysql'

    def __init__(self, db_name, db_config, tb_config):
        super().__init__(db_name, db_config, tb_config)
        self.username = db_config.pop('username')
        self.password = db_config.pop('password')

    def backup(self):
        pass