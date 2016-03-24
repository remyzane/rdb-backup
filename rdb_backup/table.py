import os


class TableProcessor(object):

    processor_name = None

    def __init__(self, db, name, define=None, selector=None):
        self.db = db
        self.name = name
        self.define = define
        self.selector = selector
        self.backup_path = db.backup_path.replace('{table_name}', name)

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


class DefaultProcessor(TableProcessor):

    processor_name = 'default'

    def backup(self):
        print(self.backup_path)
        pass

    def restore(self):
        pass


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
