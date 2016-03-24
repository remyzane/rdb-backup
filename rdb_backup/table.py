
class TableProcessor(object):

    processor_name = None

    def __init__(self, db, name, define=None, selector=None):
        self.db = db
        self.name = name
        self.define = define
        self.selector = selector

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


class DefaultProcessor(TableProcessor):

    processor_name = 'default'

    def backup(self):
        print(self.db.get_path(self.name))

    def restore(self):
        pass


class CompressProcessor(TableProcessor):

    processor_name = 'compress'


class SectionProcessor(TableProcessor):

    processor_name = 'section'


class IncrementalProcessor(TableProcessor):

    processor_name = 'incremental'

    def __init__(self):
        pass


class IncrementalCompressProcessor(TableProcessor):

    processor_name = 'incremental_compress'

    def __init__(self, compress_file_size):
        pass


# generate in rdb_backup.utility.init_processor
table_processors = {}
