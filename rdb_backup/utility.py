
import os
import yaml

from rdb_backup.processor import processor_classes

template_path = os.path.realpath(os.path.join(__file__, '..', 'template.yml'))
tests_config = os.path.realpath(os.path.join(__file__, '..', '..', 'tests', 'config_files'))


def load_yml(file_path, prefix=None):
    if prefix:
        file_path = os.path.join(prefix, file_path)
    if not os.path.exists(file_path):
        raise Exception('config file [%s] not exists.' % file_path)
    f = open(file_path, 'r', encoding='utf-8')
    conf = yaml.load(f)
    f.close()
    return conf


def get_config(file_path, prefix=None):
    """ Create config's data structure from configure file.

    :param file_path: configure file path
    :param prefix: configure file path prefix
    :return: {
        '__backup-path__': 'xxx',
        'table1': {
            'processor': 'mysql'

    """
    config = load_yml(file_path, prefix)
    ret_data = {}
    for __config_item__, __config_value__ in config.items():
        # common config
        if __config_item__ not in processor_classes:
            ret_data['__%s__' % __config_item__] = __config_value__
        # database config
        db_type, dbs = __config_item__, __config_value__
        processor_class = processor_classes[db_type]
        for db_name, db_config in dbs.items():
            print(processor_class, db_name, db_config)


