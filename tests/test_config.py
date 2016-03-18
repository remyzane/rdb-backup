
from rdb_backup.utility import get_config, tests_config, template_path


def test_template():
    dbs = get_config(template_path)
    for db in dbs:
        if db.db_name == 'database_1':
            assert db.processor_name == 'postgresql'
            assert db.__class__.__name__ == 'Postgres'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_1/{table_name}'
            assert db.ignore == 'table2 table3 log_yyyymmdd log_*'
            assert db.define == {'table_1': 'select * from table_6 where create_time > yyyymmdd'}

        if db.db_name == 'database_2':
            assert db.processor_name == 'mysql'
            assert db.__class__.__name__ == 'Mysql'
            assert db.backup_root == '/backup-root'
            assert db.backup_path == 'database_2/{table_name}'
            assert db.ignore is None

#
# def test_template2():
#     config = get_config('config.yml', tests_config)


#
# communal:
#
#   backup_root: /backup-root
#   backup_path: "{db_name}/{table_name}"   # {dbms_name}  {date_time}
#
#   #include:   # you customization database and table processor
#   #  - python_path.python_module
#
#
# dbms_1:
#   __dbms__:
#     processor: postgresql   # mysql  |  postgresql  |  defined_youself
#
#   database_1:
#     __db__:
#       ignore: "table2 table3 log_yyyymmdd log_*"
#       table_1: select * from table_6 where create_time > yyyymmdd
