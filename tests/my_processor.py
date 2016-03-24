
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor


class MyDatabaseProcessor(DatabaseProcessor):

    processor_name = 'my_processor'

    def __init__(self, dbms, name, db_config, tb_config):
        super().__init__(dbms, name, db_config, tb_config)
        self.customization_param_a = db_config.pop('customization_param_a')
        self.customization_param_b = db_config.pop('customization_param_b')

    def tables_all(self):
        return ['table_1', 'table_2', 'table_3', 'table_4', 'table_5']

    # implement in subclass
    def backup_schema(self, schema_path):
        raise NotImplementedError


class MyTableProcessor(TableProcessor):

    processor_name = 'my_processor'

    def __init__(self, db, tb_name, define=None, selector=None):
        super().__init__(db, tb_name, define, selector)
        self.customization_param1 = define.pop('customization_param1', None)
        self.customization_param2 = define.pop('customization_param2', None)

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError