from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from plpacker.cli import parse_args


class TestParseArgs(object):
    def test_defaults(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        args = vars(parse_args([]))
        assert args['archive_dir'] is None
        assert args['config_file'] is None
        assert args['excludes'] is None
        assert args['followlinks'] is None
        assert args['generate_config'] is False
        assert args['includes'] is None
        assert args['keep_archive'] is None
        assert args['keep_virtualenv'] is None
        assert args['output'] is None
        assert args['packages'] is None
        assert args['python'] is None
        assert args['requirements'] is None
        assert args['virtualenv_dir'] is None

    cli_options = (
        (['--config-file', 'config_file_path'],
         'config_file',
         'config_file_path'),
        (['--include', 'includeA'],
         'includes',
         ['includeA']),
        (['--exclude', 'exclude2', '--exclude', 'exclude1'],
         'excludes',
         ['exclude2', 'exclude1']),
        (['--followlinks'],
         'followlinks',
         True),
        (['--virtualenv-dir', 'targer_virtualenv_dir'],
         'virtualenv_dir',
         'targer_virtualenv_dir'),
        (['--keep-virtualenv'],
         'keep_virtualenv',
         True),
        (['--python', 'some_python_ver'],
         'python',
         'some_python_ver'),
        (['--requirement', 'req1',
          '--requirement', 'req2',
          '--requirement', 'req3'],
         'requirements',
         ['req1', 'req2', 'req3']),
        (['-r', 'single_req'],
         'requirements',
         ['single_req']),
        (['--package', 'package1', '--package', 'package2'],
         'packages',
         ['package1', 'package2']),
        (['--package', 'pip-package'],
         'packages',
         ['pip-package']),
        (['-p', 'another_pip_package'],
         'packages',
         ['another_pip_package']),
        (['--output', 'some_other_zip'],
         'output',
         'some_other_zip'),
        (['-o', 'some_output_file'],
         'output',
         'some_output_file'),
        (['--archive-dir', 'some_archive_dir'],
         'archive_dir',
         'some_archive_dir'),
        (['--keep-archive'],
         'keep_archive',
         True),
        (['--generate-config'],
         'generate_config',
         True),
    )

    @pytest.mark.parametrize("argv,key,expected", cli_options)
    def test_foohoo(self, argv, key, expected):
        # pylint: disable=no-self-use
        result = vars(parse_args(argv))
        assert result[key] == expected
