from rdb_backup.utility import run_psql

PG_TABLES = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"


def pg_tables(db_name):
    process = run_psql(db_name, PG_TABLES)
    out = process.stdout.readlines()
    out = out[2:-2]
    tables = []
    for item in out:
        tables.append(item.strip().decode('utf8'))
    return tables
