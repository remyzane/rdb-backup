
from rdb_backup.utility import get_config, tests_config, template_path


def test_template():
    get_config(template_path)

#
# def test_template2():
#     config = get_config('config.yml', tests_config)
