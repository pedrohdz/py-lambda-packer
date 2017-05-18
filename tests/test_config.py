from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str  # noqa pylint: disable=redefined-builtin

import copy
import os

try:
    from unittest.mock import sentinel, patch
except ImportError:
    from mock import sentinel, patch

import pytest

from plpacker.config import Configuration, CliArgInjector


class TestConfigConstructor(object):
    @patch.object(Configuration, '_load_file')
    @patch.object(Configuration, '_find_config_file')
    @patch.object(Configuration, '_merge')
    def test_default_call_flow(self, merge_mock, find_mock, load_mock):
        # pylint: disable=no-self-use
        cli_args = {'cli_args': '92VzQ'}
        find_mock.return_value = sentinel.conf_path
        load_mock.side_effect = (sentinel.work_data, sentinel.file_data)

        config = Configuration(cli_args)

        assert config.cli_args == cli_args
        assert config.defaults_file_path.endswith(
            'plpacker/conf/DEFAULT_CONFIG.yaml')
        assert config.config_file_path == sentinel.conf_path
        assert config.data == sentinel.work_data

        merge_mock.assert_called_with(sentinel.work_data,
                                      sentinel.file_data,
                                      cli_args)

    def test_default_values(self):
        # pylint: disable=no-self-use
        config = Configuration({})
        assert config.data['virtualenv']['python'] == 'python2.7'
        assert config.data['virtualenv']['path'] is None
        assert not config.data['virtualenv']['keep']
        assert config.data['virtualenv']['pip']['requirements'] == []
        assert config.data['virtualenv']['pip']['packages'] == []
        assert config.data['virtualenv']['default_excludes'] == [
            'easy_install.*',
            'pip*/**',
            'py-lambda-packer.yaml',
            'setuptools*/**',
            'wheel*/**']
        assert config.data['packager']['target'] == 'py-lambda-package.zip'
        assert config.data['packager']['build_path'] is None
        assert not config.data['packager']['keep']
        assert not config.data['packager']['followlinks']
        assert config.data['packager']['includes'] == []
        assert config.data['packager']['excludes'] == []
        assert config.data['packager']['default_excludes'] == [
            '**/*~',
            '**/*.swp',
            '**/.*.swp',
            '**/.DS_Store',
            '**/.DS_Store?',
            '**/._*',
            '**/.Spotlight-V100',
            '**/.Trashes',
            '**/Icon?',
            '**/ehthumbs.db',
            '**/Thumbs.db']

    def test_validate_schema(self):
        # pylint: disable=no-self-use
        # Poor version of scheme validation.
        config = Configuration({})
        assert sorted(config.data.keys()) == ['packager', 'virtualenv']
        assert sorted(config.data['packager'].keys()) == [
            'build_path', 'default_excludes', 'excludes', 'followlinks',
            'includes', 'keep', 'target']
        assert sorted(config.data['virtualenv'].keys()) == [
            'default_excludes', 'keep', 'path', 'pip', 'python']
        assert sorted(config.data['virtualenv']['pip'].keys()) == [
            'packages', 'requirements']


class TestConfigMergeDicts(object):
    good_merge_data = (
        ({}, {}, {}),
        ({'a': '1', 'b': '2'},
         {},
         {'a': '1', 'b': '2'}),
        ({},
         {'a': '1', 'b': '2'},
         {'a': '1', 'b': '2'}),
        ({'a': '1', 'b': '2'},
         {'a': '1', 'b': '2'},
         {'a': '1', 'b': '2'}),
        ({'a': '1', 'b': '2'},
         {'c': '3'},
         {'a': '1', 'b': '2', 'c': '3'}),
        ({'a': {'a1': '1a'}, 'b': '2'},
         {'a': {'a2': '2a'}},
         {'a': {'a1': '1a', 'a2': '2a'}, 'b': '2'}),
    )

    @pytest.mark.parametrize("left,right,expected", good_merge_data)
    def test_good_data(self, left, right, expected):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        config._merge_dicts(left, right)
        assert left == expected

    bad_merge_data = (
        ({'a': {'a1': '1a'}, 'b': '2'},
         {'a': '1'},
         'a'),
        ({'a': '1'},
         {'a': {'a1': '1a'}, 'b': '2'},
         'a'),
        ({'a': {'a1': '1a'}, 'b': '2'},
         {'a': {'a1': {}}},
         'a.a1'),
    )

    @pytest.mark.parametrize("left,right,expected", bad_merge_data)
    def test_bad_data(self, left, right, expected):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        with pytest.raises(ValueError) as info:
            config._merge_dicts(left, right)
        assert str(info.value) == \
            'Conflict at : {}'.format(expected)


class TestConfigMergeCliArgs(object):
    def test_empty_stays_empty(self):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        data_in = {}
        config._merge_cli_args({}, {})
        assert data_in == {}

    def test_no_changes(self):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        default_data_ori = copy.deepcopy(config.data)
        default_data_in = copy.deepcopy(config.data)

        config._merge_cli_args(default_data_in, {})
        assert default_data_in == default_data_ori

    def test_just_with_cli_args(self):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        cli_args = self.cli_args_sentinals()
        merged_data = {}
        config._merge_cli_args(merged_data, cli_args)

        # `cli_args_sentinals` instead of `cli_args` just for in case
        # `cli_args` was tampered with.
        cli_args_sentinals = self.cli_args_sentinals()
        assert merged_data['virtualenv']['python'] \
            == cli_args_sentinals['python']
        assert merged_data['virtualenv']['path'] \
            == cli_args_sentinals['virtualenv_dir']
        assert merged_data['virtualenv']['keep'] \
            == cli_args_sentinals['keep_virtualenv']
        assert merged_data['virtualenv']['pip']['requirements'] \
            == cli_args_sentinals['requirements']
        assert merged_data['virtualenv']['pip']['packages'] \
            == cli_args_sentinals['packages']
        assert merged_data['packager']['target'] \
            == cli_args_sentinals['output']
        assert merged_data['packager']['build_path'] \
            == cli_args_sentinals['archive_dir']
        assert merged_data['packager']['keep'] \
            == cli_args_sentinals['keep_archive']
        assert merged_data['packager']['followlinks'] \
            == cli_args_sentinals['followlinks']
        assert merged_data['packager']['includes'] \
            == cli_args_sentinals['includes']
        assert merged_data['packager']['excludes'] \
            == cli_args_sentinals['excludes']

    def test_default_data_with_cli_args(self):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        cli_args = self.cli_args_sentinals()
        merged_data = copy.deepcopy(config.data)
        config._merge_cli_args(merged_data, cli_args)

        # `cli_args_sentinals` instead of `cli_args` just for in case
        # `cli_args` was tampered with.
        cli_args_sentinals = self.cli_args_sentinals()
        assert merged_data['virtualenv']['python'] \
            == cli_args_sentinals['python']
        assert merged_data['virtualenv']['path'] \
            == cli_args_sentinals['virtualenv_dir']
        assert merged_data['virtualenv']['keep'] \
            == cli_args_sentinals['keep_virtualenv']
        assert merged_data['virtualenv']['pip']['requirements'] \
            == cli_args_sentinals['requirements']
        assert merged_data['virtualenv']['pip']['packages'] \
            == cli_args_sentinals['packages']
        assert merged_data['packager']['target'] \
            == cli_args_sentinals['output']
        assert merged_data['packager']['build_path'] \
            == cli_args_sentinals['archive_dir']
        assert merged_data['packager']['keep'] \
            == cli_args_sentinals['keep_archive']
        assert merged_data['packager']['followlinks'] \
            == cli_args_sentinals['followlinks']
        assert merged_data['packager']['includes'] \
            == cli_args_sentinals['includes']
        assert merged_data['packager']['excludes'] \
            == cli_args_sentinals['excludes']

    @patch('plpacker.config.CliArgInjector')
    def test_utilizes_injector(self, injector):
        # pylint: disable=no-self-use,protected-access
        config = Configuration({})
        config._merge_cli_args(sentinel.data, sentinel.args)
        injector.assert_called_with(sentinel.data, sentinel.args)

    @patch.object(CliArgInjector, 'map')
    def test_calls_injector_map(self, map_mock):
        # pylint: disable=protected-access
        config = Configuration({})
        cli_args = self.cli_args_sentinals()
        config._merge_cli_args({}, cli_args)
        assert map_mock.call_count == 11

    @staticmethod
    def cli_args_sentinals():
        return {
            'archive_dir': sentinel.archive_dir,
            'config_file': sentinel.config_file,
            'excludes': sentinel.excludes,
            'followlinks': sentinel.followlinks,
            'includes': sentinel.includes,
            'keep_archive': sentinel.keep_archive,
            'keep_virtualenv': sentinel.keep_virtualenv,
            'output': sentinel.output,
            'packages': sentinel.packages,
            'python': sentinel.python,
            'requirements': sentinel.requirements,
            'virtualenv_dir': sentinel.virtualenv_dir}


class TestConfigFindConfigFile(object):
    @patch('plpacker.config.expand_path')
    def test_calls_expand_path_on_valid(self, expand_path_mock):
        # pylint: disable=no-self-use,protected-access
        expand_path_mock.return_value = sentinel.expanded_path
        config = Configuration({})

        path = config._find_config_file(sentinel.config_file_path)

        assert path == sentinel.expanded_path
        expand_path_mock.assert_called_with(sentinel.config_file_path, True)

    @patch.object(Configuration, '_load_file')
    def test_returns_config_in_cwd(self, load_file_mock, source_fs):
        # pylint: disable=no-self-use,protected-access,unused-argument
        load_file_mock.return_value = {}
        os.chdir('/home/foo/src/bar-project')
        config = Configuration({})

        path = config._find_config_file(None)
        assert path == '/home/foo/src/bar-project/py-lambda-packer.yaml'

    @patch.object(Configuration, '_load_file')
    def test_nothing_found(self, load_file_mock, source_fs):
        # pylint: disable=no-self-use,protected-access,unused-argument
        load_file_mock.return_value = {}
        os.chdir('/home')
        config = Configuration({})

        path = config._find_config_file(None)
        assert path is None


class TestConfigMerge(object):
    @patch.object(Configuration, '_merge_cli_args')
    @patch.object(Configuration, '_merge_dicts')
    def test_everything_provided(self, merge_dicts_mock, merge_cli_args_mock):
        # pylint: disable=no-self-use,protected-access
        merge_dicts_mock.return_value = sentinel.merge_dicts
        merge_cli_args_mock.return_value = sentinel.merge_cli_args

        config = Configuration({})
        config._merge(sentinel.work_data, sentinel.file_data,
                      sentinel.cli_args)

        merge_dicts_mock.assert_called_with(sentinel.work_data,
                                            sentinel.file_data)
        merge_cli_args_mock.assert_called_with(sentinel.work_data,
                                               sentinel.cli_args)

    @patch.object(Configuration, '_merge_cli_args')
    @patch.object(Configuration, '_merge_dicts')
    def test_file_data_missing(self, merge_dicts_mock, merge_cli_args_mock):
        # pylint: disable=no-self-use,protected-access
        merge_cli_args_mock.return_value = sentinel.merge_cli_args

        config = Configuration({})
        config._merge(sentinel.work_data, None, sentinel.cli_args)

        merge_dicts_mock.assert_not_called()
        merge_cli_args_mock.assert_called_with(sentinel.work_data,
                                               sentinel.cli_args)

    @patch.object(Configuration, '_merge_cli_args')
    @patch.object(Configuration, '_merge_dicts')
    def test_cli_args_missing(self, merge_dicts_mock, merge_cli_args_mock):
        # pylint: disable=no-self-use,protected-access
        merge_cli_args_mock.return_value = sentinel.merge_cli_args

        config = Configuration({})
        config._merge(sentinel.work_data, sentinel.file_data, None)

        merge_dicts_mock.assert_called_with(sentinel.work_data,
                                            sentinel.file_data)
        merge_cli_args_mock.assert_not_called()

    @patch.object(Configuration, '_merge_cli_args')
    @patch.object(Configuration, '_merge_dicts')
    def test_everything_missing(self, merge_dicts_mock, merge_cli_args_mock):
        # pylint: disable=no-self-use,protected-access
        merge_cli_args_mock.return_value = sentinel.merge_cli_args

        config = Configuration({})
        config._merge(sentinel.work_data, None, None)

        merge_dicts_mock.assert_not_called()
        merge_cli_args_mock.assert_not_called()
