
class TableProcessor(object):

    # def __init__(self):
    #     pass

    def backup(self):
        pass

    def restore(self):
        pass


class DefaultProcessor(TableProcessor):

    name = 'default'

    def backup(self):
        pass


class CompressProcessor(TableProcessor):

    name = 'compress'


class SectionProcessor(TableProcessor):

    name = 'section'


class IncrementalProcessor(TableProcessor):

    name = 'incremental'

    def __init__(self):
        pass


class IncrementalCompressProcessor(TableProcessor):

    name = 'incremental_compress'

    def __init__(self, compress_file_size):
        pass


# generate in rdb_backup.utility.init_processor
table_classes = {}
