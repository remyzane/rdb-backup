
from rdb_backup.utility import get_config, template_path


def test_template():
    dbs = get_config(template_path)
    for db in dbs:
        if db.db_name == 'database_1':
            assert db.processor_name == 'postgresql'
            assert db.__class__.__name__ == 'PostgresLocal'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_1/{table_name}'
            assert db.ignore == 'table3 log_yyyymmdd log_*'
            table1 = db.define['table_1']
            assert table1.db == db
            assert table1.tb_name == 'table_1'
            assert table1.selector == 'select * from table_1 where create_time > yyyymmdd'

        if db.db_name == 'database_2':
            assert db.processor_name == 'mysql'
            assert db.__class__.__name__ == 'MysqlLocal'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_2/{table_name}'
            assert db.ignore is None
            table2 = db.define['table_2']
            assert table2.db == db
            assert table2.tb_name == 'table_2'
            assert table2.selector == 'select * from table_2 where create_time > yyyymmdd'
