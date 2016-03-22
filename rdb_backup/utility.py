import os
import time
import yaml
import copy
import random
import string
import subprocess
from importlib import import_module

template_path = os.path.realpath(os.path.join(__file__, '..', 'template.yml'))
tests_config = os.path.realpath(os.path.join(__file__, '..', '..', 'tests', 'config_files'))


class ProcessorNonexistent(Exception):
    pass


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
    from rdb_backup.table import table_processors, TableProcessor
    from rdb_backup.database import database_processors, DatabaseProcessor
    from rdb_backup.mysql import MysqlLocal         # regist in DatabaseProcessor's __subclasses__
    from rdb_backup.postgres import PostgresLocal   # regist in DatabaseProcessor's __subclasses__

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
    from rdb_backup.database import database_processors
    config = load_yml(file_path, prefix)

    # communal config
    communal_config = config.pop('communal')
    init_processor(communal_config.pop('include', []))

    # dbms config
    databases = []
    for dbms_name, dbs in config.items():
        dbms_params = dbs.pop('__dbms__')
        dbms_processor = dbms_params.pop('processor')
        dbms_config = copy.deepcopy(dbms_params)
        dbms_config.update(copy.deepcopy(communal_config))
        dbms_config['backup_path'] = dbms_config['backup_path'].replace('{dbms_name}', dbms_name)

        processor_class = database_processors.get(dbms_processor)
        if not processor_class:
            raise ProcessorNonexistent('database processor [%s] nonexistent.' % dbms_processor)
        for db_name, tbs in dbs.items():
            db_params = tbs.pop('__db__', {}) if tbs else {}
            db_config = copy.deepcopy(db_params)
            db_config.update(copy.deepcopy(dbms_config))
            db_config['backup_path'] = db_config['backup_path'].replace('{db_name}', db_name)
            database = processor_class(db_name, db_config, tbs)
            databases.append(database)
    return databases


def run_shell(user, content, cwd='/tmp'):
    file_path = '/tmp/' + ''.join(random.sample(string.ascii_letters, 20))
    content = '#! /bin/sh%s%s' % (os.linesep, content)
    with open(file_path, 'w') as file:
        file.write(content)
    os.system('chmod og+rx ' + file_path)
    process = subprocess.Popen('su %s -c %s' % (user, file_path), shell=True, stdout=subprocess.PIPE, cwd=cwd)
    time.sleep(1)
    os.unlink(file_path)
    return process


def run_psql(db, sql, cwd='/tmp'):
    content = 'psql %s -c "%s"' % (db, sql)
    return run_shell('postgres', content, cwd)
