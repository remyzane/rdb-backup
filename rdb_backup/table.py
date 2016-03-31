

class TableProcessor(object):

    processor_name = None

    def __init__(self, db, name, define=None):  # , selector=None):
        self.db = db
        self.name = name
        self.define = define
        # self.selector = selector
        self.backup_path = db.backup_path.replace('{table_name}', name)
        self.field_names = None

    @staticmethod
    def transform_data(value, date_type):
        return date_type(value)

    def set_field_names(self, names):
        self.field_names = names

    def get_field(self, record, field_name, data_type):
        value = record[self.field_names.index(field_name)]
        return self.transform_data(value, data_type)

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


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
