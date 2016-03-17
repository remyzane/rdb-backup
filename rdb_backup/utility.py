
import os
import yaml
import copy
from importlib import import_module

from rdb_backup.table import table_classes, TableProcessor
from rdb_backup.database import database_classes, DatabaseProcessor

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

    for table_class in TableProcessor.__subclasses__():
        table_classes[table_class.name] = table_class

    for database_class in DatabaseProcessor.__subclasses__():
        database_classes[database_class.name] = database_class


def get_config(file_path, prefix=None):
    """ Create config's data structure from configure file.

    :param file_path: configure file path
    :param prefix: configure file path prefix
    :return: {
        '__backup_path__': 'xxx',
        'table1': {
            'processor': 'mysql'

    """
    config = load_yml(file_path, prefix)

    # communal config
    communal_config = config.pop('communal')
    init_processor(communal_config.pop('include', []))

    # dbms config
    databases = []
    for dbms_name, dbs in config.items():
        dbms_params = dbs.pop('__dbms__')
        dbms_class = dbms_params.pop['processor']
        dbms_config = copy.deepcopy(dbms_params)
        dbms_config.update(copy.deepcopy(communal_config))
        dbms_config['backup_path'] = dbms_config['backup_path'].replace('{dbms_name}', dbms_name)

        db_class = database_classes[dbms_class]
        for db_name, tbs in dbs.items():
            db_params = tbs.pop('__db__')
            db_config = copy.deepcopy(db_params)
            db_config.update(copy.deepcopy(dbms_config))
            db_config['backup_path'] = db_config['backup_path'].replace('{db_name}', db_name)

            database = db_class(db_name, db_config)
            database.backup()
            databases.append(database)
    return databases
