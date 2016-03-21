import os

from rdb_backup.postgres import pg_tables
from rdb_backup.utility import get_config, tests_config


def test_processor_customize():
    dbs = get_config('postgres.yml', tests_config)
    for db in dbs:
        print(db.db_name)
        for table_name in pg_tables(db.db_name):
            print(table_name)

        # if db.db_name == 'database_1':
        #     assert db.processor_name == 'my_db_processor'
        #     assert db.__class__.__name__ == 'MyDatabaseProcessor'
        #     assert db.customization_param_a == 'aaa'
        #     assert db.customization_param_b == 'bbb'
        #     table1 = db.define['table_1']
        #     assert table1.db == db
        #     assert table1.tb_name == 'table_1'
        #     assert table1.processor_name == 'my_tb_processor'
        #     assert table1.__class__.__name__ == 'MyTableProcessor'
        #     assert table1.customization_param1 == 'xxx'
        #     assert table1.customization_param2 == 'yyy'








print(pg_tables('database_1'))


def _backup():

    savepath = '/mnt/bkup/sql'

    sqldir = '/var/lib/postgresql/sql'
    databases = []
    for database in databases:
        os.system("su postgres -c 'cd %s && pg_dump %s > %s._sql_'" % (sqldir, database, database))
        os.system("mv %s/%s._sql_ %s/%s.sql" % (sqldir, database, savepath, database))
        os.system("chown root:root %s/%s.sql" % (savepath, database))
        os.system("chmod og-rwx %s/%s.sql" % (savepath, database))

    user = 'root'
    password = 'gaau_xddc_ddvp_1775'
    databases = ['conosoft_sms', ]
    for database in databases:
        ret = os.system("mysqldump -u %s -p'%s' %s > %s/%s.tmp" % (user, password, database, savepath, database))
        if ret == 0:
            os.system("mv %s/%s.tmp %s/%s.sql" % (savepath, database, savepath, database))
            os.system("chmod og-rwx %s/%s.sql" % (savepath, database))
        else:
            os.system("rm %s/%s.tmp" % (savepath, database))


