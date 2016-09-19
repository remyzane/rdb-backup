import os
import logging
from datetime import datetime

from rdb_backup.utility import ProcessorNonexistent

log = logging.getLogger(__name__)


class DatabaseProcessor(object):

    processor_name = None

    def __init__(self, dbms, name, db_config, tb_config):
        self.dbms = dbms
        self.name = name
        self.backup_root = db_config.pop('backup_root')
        self.backup_path = self.__get_path(db_config.pop('backup_path'))
        self.ignore_list = db_config.pop('ignore', '').split()
        self.define = {}    # table define
        self.debug = db_config.get('debug', False)

        db_path = self.backup_path.split('{table_name}')[0]
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.schema_sql = os.path.join(db_path, '__schema__.sql')

        for tb_name, define in tb_config.items():
            table_processor = self.processor_name
            params = None
            if type(define) == dict:
                table_processor = define.pop('processor', self.processor_name)
                params = define

            processor_class = table_processors.get(table_processor)
            if not processor_class:
                raise ProcessorNonexistent('table processor [%s] nonexistent.' % table_processor)

            self.define[tb_name] = processor_class(self, tb_name, params)

    def ignored(self, name):
        for item in self.ignore_list:
            if item[-1] == '*':
                if name.startswith(item[:-1]):
                    return True
                else:
                    return False
            elif item == name:
                return True
        return False

    def __get_path(self, backup_path):
        backup_path = backup_path.replace('{dbms_name}', self.dbms)
        backup_path = backup_path.replace('{db_name}', self.name)
        backup_path = backup_path.replace('{date_time}', datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        return os.path.join(self.backup_root, backup_path)

    def tables_need_backup(self):
        tables = {}
        tables_ignored = []
        table_names = self.table_names()
        for table_name in self.define.keys():
            if table_name not in table_names:
                raise IndexError('defined table [%s] is not exists in database [%s]' % (table_name, self.name))

        for table_name in table_names:
            if self.ignored(table_name):
                tables_ignored.append(table_name)
            else:
                if table_name in self.define:
                    tables[table_name] = self.define[table_name]
                else:
                    tables[table_name] = table_processors[self.processor_name](self, table_name, {})
        if tables_ignored:
            log.info('ignored tables: %s' % tables_ignored)
        return tables

    # implement in subclass ---------------------------------

    def table_names(self):
        raise NotImplementedError

    def backup(self, need_backup_tables):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


class TableProcessor(object):

    processor_name = None

    def __init__(self, db, name, define=None):
        self.db = db
        self.name = name
        self.backup_path = db.backup_path.replace('{table_name}', name)
        self.field_names = None
        self.file = None
        if not define:
            self.define = dict()
            self.filter = None
        else:
            self.define = define
            self.filter = self.define.get('filter', None)
        if self.filter:
            if not ('>' in self.filter or '<' in self.filter or '=' in self.filter):
                raise SyntaxError('unknown filter syntax [%s] in %s.%s, filter only support [>, <, =]' %
                                  (self.filter, self.db.name, self.name))
            self.filter = self.filter.split(maxsplit=2)

    def set_field_names(self, names):
        self.field_names = names

    def add_field_name(self, name):
        self.field_names.append(name)

    def get_field(self, record, field_name):
        try:
            return record[self.field_names.index(field_name)]
        except ValueError:
            raise IndexError('defined field name [%s] not exists in table [%s.%s]' % (field_name, self.db.name, self.name))

    def close(self):
        self.file.close()
        statinfo = os.stat(self.backup_path)
        size = statinfo.st_size
        if size == 0:
            size_string = '0'
        else:
            size = size / 1048576.0     # 1048576 = 1024 * 1024
            if size > 99999:
                size_string = 'FFFFF'
            elif size < 1:
                size_string = '.'
            else:
                size_string = str(int(size))
        log.info('backup %s MB %s', size_string.rjust(5), self.backup_path)


# generate in rdb_backup.utility.init_processor
database_processors = {}
table_processors = {}


#
# class CompressProcessor(TableProcessor):
#
#     processor_name = 'compress'
#
#     def backup(self):
#         pass
#
#     def restore(self):
#         pass
#
#
# class SectionProcessor(TableProcessor):
#
#     processor_name = 'section'
#
#     def backup(self):
#         pass
#
#     def restore(self):
#         pass
#
#
# class IncrementalProcessor(TableProcessor):
#
#     processor_name = 'incremental'
#
#     def backup(self):
#         pass
#
#     def restore(self):
#         pass
#
#
# class IncrementalCompressProcessor(TableProcessor):
#
#     processor_name = 'incremental_compress'
#
#     def __init__(self, compress_file_size):
#         pass
#
#     def backup(self):
#         pass
#
#     def restore(self):
#         pass
