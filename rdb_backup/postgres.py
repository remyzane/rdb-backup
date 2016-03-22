from rdb_backup.utility import run_psql
from rdb_backup.database import DatabaseProcessor

PG_TABLES = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgres'

    def tables_all(self):
        process = run_psql(self.db_name, PG_TABLES)
        out = process.stdout.readlines()
        out = out[2:-2]
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables
