from rdb_backup.utility import get_config, tests_config


def test_processor_customize():
    print('----')
    communal_config, dbs = get_config('postgres.yml', tests_config)
    for db in dbs:
        db.backup(db.tables_need_backup())
