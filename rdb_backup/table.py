
class TableProcessor(object):

    processor_name = None

    def __init__(self, db, tb_name, define=None, selector=None):
        self.db = db
        self.tb_name = tb_name
        self.selector = selector

    def backup(self):
        pass

    def restore(self):
        pass


class DefaultProcessor(TableProcessor):

    processor_name = 'default'

    def backup(self):
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
