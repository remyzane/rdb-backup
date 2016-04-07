
from rdb_backup.processor import TableProcessor, DatabaseProcessor


class MyDatabaseProcessor(DatabaseProcessor):

    processor_name = 'my_processor'

    def __init__(self, dbms, name, db_config, tb_config):
        super().__init__(dbms, name, db_config, tb_config)
        self.customization_param_a = db_config.pop('customization_param_a')
        self.customization_param_b = db_config.pop('customization_param_b')

    def table_names(self):
        return ['table_1', 'table_2', 'table_3', 'table_4', 'table_5']

    # implement in subclass
    def dump_data(self, schema_path):
        raise NotImplementedError


class MyTableProcessor(TableProcessor):

    processor_name = 'my_processor'

    def __init__(self, db, tb_name, define=None):
        super().__init__(db, tb_name, define)
        self.customization_param1 = define.pop('customization_param1', None)
        self.customization_param2 = define.pop('customization_param2', None)

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError