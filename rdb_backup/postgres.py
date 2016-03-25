import os

from rdb_backup.utility import run_shell
from rdb_backup.table import TableProcessor
from rdb_backup.database import DatabaseProcessor

QUERY_TABLES_SQL = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"


class PostgresLocal(DatabaseProcessor):

    processor_name = 'postgres'

    tmp_dir = '/tmp/rdb_backup_postgres_local'
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    run_shell('chown postgres:postgres %s' % tmp_dir)
    run_shell('chmod og-rwx %s' % tmp_dir)

    @classmethod
    def run_psql(cls, db, sql):
        command = 'psql %s -c "%s"' % (db, sql)
        return run_shell(command, 'postgres', cwd=cls.tmp_dir)

    def tables_all(self):
        process = self.run_psql(self.name, QUERY_TABLES_SQL)
        out = process.stdout.readlines()
        out = out[2:-2]
        tables = []
        for item in out:
            tables.append(item.strip().decode('utf8'))
        return tables

    def backup_schema(self, schema_path):
        tmp_path = os.path.join(self.tmp_dir, '__%s__schema__.sql' % self.name)
        run_shell('pg_dump %s > %s' % (self.name, tmp_path), 'postgres', cwd=self.tmp_dir)
        # TODO dump all db then  split table

        run_shell('mv %s %s' % (tmp_path, schema_path))
        run_shell('chown root:root %s' % schema_path)


class PostgresTable(TableProcessor):

    processor_name = 'postgres'

    def backup(self):

        tmp_path = os.path.join(self.db.tmp_dir, '%s.sql' % self.name)

        run_shell('pg_dump -t %s %s > %s' % (self.name, self.db.name, tmp_path), 'postgres', cwd=self.db.tmp_dir)
        run_shell('mv %s %s' % (tmp_path, self.backup_path + '.sql'))
        run_shell('chown root:root %s' % self.backup_path + '.sql')

        print(self.backup_path + '.sql')
        pass

    def restore(self):
        pass
