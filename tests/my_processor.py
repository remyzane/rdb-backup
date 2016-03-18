
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor


class MyDatabaseProcessor(DatabaseProcessor):

    processor_name = 'my_db_processor'

    def __init__(self, db_name, db_config, tb_config):
        super().__init__(db_name, db_config, tb_config)
        self.customization_param_a = db_config.pop('customization_param_a')
        self.customization_param_b = db_config.pop('customization_param_b')


class MyTableProcessor(TableProcessor):

    processor_name = 'my_tb_processor'

    def __init__(self, db, tb_name, define=None, selector=None):
        super().__init__(db, tb_name, define, selector)
        self.customization_param1 = define.pop('customization_param1')
        self.customization_param2 = define.pop('customization_param2')
