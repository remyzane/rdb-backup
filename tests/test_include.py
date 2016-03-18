
from rdb_backup.utility import get_config, tests_config


def test_include_ok():
    dbs = get_config('include_ok.yml', tests_config)
    for db in dbs:
        if db.db_name == 'database_1':
            assert db.processor_name == 'my_db_processor'
            assert db.__class__.__name__ == 'MyDatabaseProcessor'
            assert db.customization_param_a == 'aaa'
            assert db.customization_param_b == 'bbb'
            table1 = db.define['table_1']
            assert table1.db == db
            assert table1.tb_name == 'table_1'
            assert table1.processor_name == 'my_tb_processor'
            assert table1.__class__.__name__ == 'MyTableProcessor'
            assert table1.customization_param1 == 'xxx'
            assert table1.customization_param2 == 'yyy'
