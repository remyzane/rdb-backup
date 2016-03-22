import os
import sys
import time
import yaml
import copy
import random
import string
import logging
import subprocess
from importlib import import_module
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

POSIX = os.name != 'nt'
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

    import_module('rdb_backup.mysql')
    import_module('rdb_backup.postgres')
    processor_paths = processor_paths + []
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

    # logging config
    log_config = config.pop('logging', None)
    if log_config:
        set_logging(log_config, os.getcwd())

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


def multiply(expression):
    """multiplication calculation

    :param expression: string e.g. "1024*1024*50"
    :return: integer
    """
    value = 1
    for n in expression.split('*'):
        value *= int(n)
    return value


class CustomizeLog(logging.Formatter):
    def __init__(self, fmt=None, date_fmt=None):
        logging.Formatter.__init__(self, fmt, date_fmt)

    def format(self, record):
        if record.levelname == 'WARNING': record.levelname = 'WARN '
        if record.levelname == 'CRITICAL': record.levelname = 'FATAL'
        record.levelname = record.levelname.ljust(5)
        return logging.Formatter.format(self, record)


def set_logging(config, root_path=''):
    """setting logging

    :param config: config dict
    :param root_path:
    """
    default_format = CustomizeLog(config['format'])
    handlers = {}

    # console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(default_format)
    handlers['stream'] = handler

    # customize handler
    for handler_name, params in config['handler'].items():
        handler_format = CustomizeLog(params['format']) if params.get('format') else default_format
        handler_params = config['class'][params['class']].copy()
        handler_params.update(params)
        # create log dir
        logfile = params['path'] if params['path'].startswith('/') else os.path.join(root_path, params['path'])
        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        # create handler
        backup_count = handler_params['backup_count']
        # which switches from one file to the next when the current file reaches a certain size.
        if params['class'] == 'rotating_file':
            max_size = multiply(handler_params['max_size'])
            handler = RotatingFileHandler(logfile, 'a', max_size, backup_count, encoding='utf-8')
        # rotating the log file at certain timed intervals.
        elif params['class'] == 'time_rotating_file':
            when = handler_params['when']
            interval = handler_params['interval']
            handler = TimedRotatingFileHandler(logfile, when, interval, backup_count, encoding='utf-8')
        handler.setFormatter(handler_format)
        handlers[handler_name] = handler

    for module, params in config['logger'].items():
        level = params['level'].upper()
        handler_names = params['handler'].split()
        propagate = params.get('propagate') or config['propagate']

        if module == 'default':                 # define root log
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(module)  # define module's logging
            logger.propagate = propagate        # judge whether repeatedly output to default logger

        for handler_name in handler_names:
            logger.addHandler(handlers[handler_name])
        logger.setLevel(level)
