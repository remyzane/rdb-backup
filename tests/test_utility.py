import os
from pathlib import Path
from unittest import mock

from rdb_backup.utility import run_shell, TMP_SHELL_FILE_PREFIX


def test_run_shell():
    p = Path(os.path.dirname(TMP_SHELL_FILE_PREFIX))
    if list(p.glob(os.path.basename(TMP_SHELL_FILE_PREFIX) + '*')):
        os.system('rm %s*' % TMP_SHELL_FILE_PREFIX)
    with mock.patch('os.unlink'):
        # run shell as command
        process = run_shell('echo "aaa"')
        out = process.stdout.readlines()
        assert out[0] == b'aaa\n'

        # run shell as command
        process = run_shell(''' echo 'aa"a' ''')
        out = process.stdout.readlines()
        assert out[0] == b'aa"a\n'
        assert list(p.glob(os.path.basename(TMP_SHELL_FILE_PREFIX) + '*')) == []

        # run shell as file
        process = run_shell('echo "aaa" %s echo "bbb"' % os.linesep)
        out = process.stdout.readlines()
        assert out[0] == b'aaa\n'
        assert out[1] == b'bbb\n'
        assert list(p.glob(os.path.basename(TMP_SHELL_FILE_PREFIX) + '*')) != []
        os.system('rm %s*' % TMP_SHELL_FILE_PREFIX)

        # run shell as file
        process = run_shell('''echo 'aa"a' ''', 'postgres')
        out = process.stdout.readlines()
        assert out[0] == b'aa"a\n'
        assert list(p.glob(os.path.basename(TMP_SHELL_FILE_PREFIX) + '*')) != []
        os.system('rm %s*' % TMP_SHELL_FILE_PREFIX)
