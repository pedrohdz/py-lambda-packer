from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str  # noqa pylint: disable=redefined-builtin

import logging
import os

import pkg_resources
import yaml

from plpacker.utils import expand_path


LOGGER = logging.getLogger(__name__)


class Configuration(object):
    # pylint: disable=too-few-public-methods
    DEFAULT_CONFIG = pkg_resources.resource_filename(
        __name__, 'conf/DEFAULT_CONFIG.yaml')

    def __init__(self, cli_args):
        self.cli_args = cli_args
        self.defaults_file_path = Configuration.DEFAULT_CONFIG
        self.config_file_path = self._find_config_file(
            cli_args.get('config_file_path', None))

        # Remember `work_data` will get mutated, a lot, before saving.
        work_data = self._load_file(self.defaults_file_path)
        file_data = (self._load_file(self.config_file_path)
                     if self.config_file_path
                     else None)

        self._merge(work_data, file_data, cli_args)
        self.data = work_data

    def _merge(self, work_data, file_data, cli_args):
        if file_data:
            self._merge_dicts(work_data, file_data)
        if cli_args:
            self._merge_cli_args(work_data, cli_args)

    @staticmethod
    def _merge_cli_args(ori_dict, cli_args):
        injector = CliArgInjector(ori_dict, cli_args)
        injector.map('packager.build_path', 'archive_dir')
        injector.map('packager.excludes', 'excludes')
        injector.map('packager.followlinks', 'followlinks')
        injector.map('packager.includes', 'includes')
        injector.map('packager.keep', 'keep_archive')
        injector.map('packager.target', 'output')
        injector.map('virtualenv.keep', 'keep_virtualenv')
        injector.map('virtualenv.path', 'virtualenv_dir')
        injector.map('virtualenv.pip.packages', 'packages')
        injector.map('virtualenv.pip.requirements', 'requirements')
        injector.map('virtualenv.python', 'python')

    def _merge_dicts(self, left, right, path=None):
        """
        Merges right into left.  Credit goes to:
            - https://stackoverflow.com/a/7205107/2721824
        """
        if path is None:
            path = []
        for key in right:
            if key in left:
                if (isinstance(left[key], dict)
                        and isinstance(right[key], dict)):
                    self._merge_dicts(left[key], right[key], path + [str(key)])
                elif left[key] == right[key]:
                    # same leaf value
                    pass
                elif (isinstance(left[key], (list, tuple))
                      and isinstance(right[key], (list, tuple))):
                    # TODO - Add unit tests
                    # Let us make a copy to be safe (shallow).
                    left[key] = [item for item in right[key]]
                elif (isinstance(left[key], (str, int, float))
                      and isinstance(right[key], (str, int, float))):
                    # TODO - Add unit tests
                    left[key] = right[key]
                else:
                    raise ValueError('Conflict at : {}'.format(
                        '.'.join(path + [str(key)])))
            else:
                left[key] = right[key]

    @staticmethod
    def _find_config_file(config_file_path):
        if config_file_path:
            return expand_path(config_file_path, True)
        local_file = os.path.join(os.getcwd(), 'py-lambda-packer.yaml')
        if os.path.exists(local_file):
            return local_file
        return None

    @staticmethod
    def _load_file(file_path):
        LOGGER.info('Loading configuration from: %s', file_path)
        with open(file_path, 'r') as stream:
            return yaml.load(stream)

    @classmethod
    def print_default_config(cls):
        with open(cls.DEFAULT_CONFIG, 'r') as config:
            print(config.read())


class CliArgInjector(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, config, cli_args):
        super(CliArgInjector, self).__init__()
        self.config = config
        self.cli_args = cli_args

    def map(self, ori_dict_key, cli_args_key):
        ori_dict_keys = ori_dict_key.split('.')

        if (cli_args_key in self.cli_args
                and self.cli_args[cli_args_key] is not None):
            current = self.config
            for key in ori_dict_keys[0:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[ori_dict_keys[-1]] = self.cli_args[cli_args_key]


def get_configuration(cli_args):
    return Configuration(cli_args)
