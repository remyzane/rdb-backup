from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor


class MysqlLocal(DatabaseProcessor):

    processor_name = 'mysql'

    def __init__(self, dbms, name, db_config, tb_config):
        super().__init__(dbms, name, db_config, tb_config)
        self.password = db_config.pop('password')
        self.username = db_config.pop('username')

    def backup(self):
        pass


class PostgresTable(TableProcessor):

    processor_name = 'mysql'

    def backup(self):
        pass

    def restore(self):
        pass
