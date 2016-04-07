import os

from rdb_backup.utility import get_config, tests_config


def test_processor_customize():
    print('----')
    communal_config, dbs = get_config('postgres.yml', tests_config)
    for db in dbs:
        db.backup()



def _backup():

    savepath = '/mnt/bkup/sql'
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
