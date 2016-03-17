
from rdb_backup.utility import get_config, tests_config


def test_include_ok():
    get_config('include_ok.yml', tests_config)

