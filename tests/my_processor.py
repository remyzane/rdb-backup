
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor


class MyTableProcessor(TableProcessor):

    processor_name = 'my_tb_processor'


class MyDatabaseProcessor(DatabaseProcessor):

    processor_name = 'my_db_processor'
