
import os
import yaml
import copy
from importlib import import_module

from rdb_backup.table import table_processors, TableProcessor
from rdb_backup.database import database_processors, DatabaseProcessor

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


def init_processor(processor_paths):
    for processor_path in processor_paths:
        import_module(processor_path)

    for table_processor in TableProcessor.__subclasses__():
        if table_processor.processor_name is None:
            raise NotImplementedError('member [processor_name] is not defined in %s' % table_processor)
        table_processors[table_processor.processor_name] = table_processor

    for database_processor in DatabaseProcessor.__subclasses__():
        if database_processor.processor_name is None:
            raise NotImplementedError('member [processor_name] is not defined in %s' % database_processor)
        database_processors[database_processor.processor_name] = database_processor


def get_config(file_path, prefix=None):
    """ Create config's data structure from configure file.

    :param file_path: configure file path
    :param prefix: configure file path prefix
    """
    config = load_yml(file_path, prefix)

    # communal config
    communal_config = config.pop('communal')
    init_processor(communal_config.pop('include', []))

    # dbms config
    databases = []
    for dbms_name, dbs in config.items():
        dbms_params = dbs.pop('__dbms__')
        dbms_class = dbms_params.pop('processor')
        dbms_config = copy.deepcopy(dbms_params)
        dbms_config.update(copy.deepcopy(communal_config))
        dbms_config['backup_path'] = dbms_config['backup_path'].replace('{dbms_name}', dbms_name)

        processor_class = database_processors[dbms_class]
        for db_name, tbs in dbs.items():
            db_params = tbs.pop('__db__', {}) if tbs else {}
            db_config = copy.deepcopy(db_params)
            db_config.update(copy.deepcopy(dbms_config))
            db_config['backup_path'] = db_config['backup_path'].replace('{db_name}', db_name)
            database = processor_class(db_name, db_config, tbs)
            databases.append(database)
    return databases
