import pytest

from rdb_backup.utility import get_config, template_path, tests_config, ProcessorNonexistent


def test_template():
    dbs = get_config(template_path)
    for db in dbs:
        if db.name == 'database_1':
            assert db.processor_name == 'postgres'
            assert db.__class__.__name__ == 'PostgresLocal'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_1/{table_name}'
            assert db.ignore_list == ['table3', 'log_yyyymmdd', 'log_*']
            table1 = db.define['table_1']
            assert table1.db == db
            assert table1.name == 'table_1'
            assert table1.selector == 'select * from table_1 where create_time > yyyymmdd'

        if db.name == 'database_2':
            assert db.processor_name == 'mysql'
            assert db.__class__.__name__ == 'MysqlLocal'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_2/{table_name}'
            assert db.ignore_list == []
            table2 = db.define['table_2']
            assert table2.db == db
            assert table2.name == 'table_2'
            assert table2.selector == 'select * from table_2 where create_time > yyyymmdd'


def test_processor_customize():
    dbs = get_config('processor_customize.yml', tests_config)
    for db in dbs:
        if db.name == 'database_1':
            assert db.processor_name == 'my_db_processor'
            assert db.__class__.__name__ == 'MyDatabaseProcessor'
            assert db.customization_param_a == 'aaa'
            assert db.customization_param_b == 'bbb'
            table1 = db.define['table_1']
            assert table1.db == db
            assert table1.name == 'table_1'
            assert table1.processor_name == 'my_tb_processor'
            assert table1.__class__.__name__ == 'MyTableProcessor'
            assert table1.customization_param1 == 'xxx'
            assert table1.customization_param2 == 'yyy'


def test_processor_nonexistent():
    pytest.raises(ProcessorNonexistent, get_config, 'processor_nonexistent1.yml', tests_config)
    pytest.raises(ProcessorNonexistent, get_config, 'processor_nonexistent2.yml', tests_config)
