

class TableProcessor(object):

    processor_name = None

    def __init__(self, db, name, define=None):
        self.db = db
        self.name = name
        self.define = define or dict()
        self.backup_path = db.backup_path.replace('{table_name}', name)
        self.field_names = None
        self.file = None
        self.filter = define.get('filter', None)
        if self.filter:
            if not ('>' in self.filter or '>' in self.filter or '=' in self.filter):
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

    #
    # def restore(self):
    #     raise NotImplementedError


class CompressProcessor(TableProcessor):

    processor_name = 'compress'

    def backup(self):
        pass

    def restore(self):
        pass


class SectionProcessor(TableProcessor):

    processor_name = 'section'

    def backup(self):
        pass

    def restore(self):
        pass


class IncrementalProcessor(TableProcessor):

    processor_name = 'incremental'

    def backup(self):
        pass

    def restore(self):
        pass


class IncrementalCompressProcessor(TableProcessor):

    processor_name = 'incremental_compress'

    def __init__(self, compress_file_size):
        pass

    def backup(self):
        pass

    def restore(self):
        pass


# generate in rdb_backup.utility.init_processor
table_processors = {}
