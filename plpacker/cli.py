from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import logging
import logging.config
import os
import sys

import pkg_resources
import yaml

from plpacker.config import Configuration
from plpacker.virtualenv import VirtualEnv
from plpacker.packager import Packager
from plpacker.fileset import FileSet
from plpacker.pylambdapacker import PyLambdaPacker


LOGGER = logging.getLogger()


def setup_logging():
    file_path = pkg_resources.resource_filename(__name__, 'conf/logging.yaml')
    with open(file_path, 'r') as stream:
        logging.config.dictConfig(yaml.load(stream))
    LOGGER.info('Logging configuration read from "%s".', file_path)


def parse_args(*argv):
    parser = argparse.ArgumentParser(description='TODO')

    parser.add_argument('--config-file',
                        dest='config_file',
                        default=None,
                        help=('location of configuration file (default: '
                              './py-lambda-packer.yaml)'))

    parser.add_argument('--include',
                        dest='includes',
                        action='append',
                        default=None,
                        help=('glob pattern of what to include, multiple '
                              'allowed (default is empty)'))

    parser.add_argument('--exclude',
                        dest='excludes',
                        action='append',
                        default=None,
                        help=('glob pattern of what to exclude, multiple '
                              'allowed (default is empty)'))

    parser.add_argument('--followlinks',
                        dest='followlinks',
                        action='store_true',
                        default=None,
                        help=('follows symbolic links (default=False)'))

    parser.add_argument('--virtualenv-dir',
                        dest='virtualenv_dir',
                        default=None,
                        help=('directory to build the virtualenv in '
                              '(default is a tmp dir)'))

    parser.add_argument('--keep-virtualenv',
                        dest='keep_virtualenv',
                        default=None,
                        action='store_true',
                        help=('do not delete virtualenv build directory when '
                              'set (default=False)'))

    parser.add_argument('--python',
                        dest='python',
                        default=None,
                        help=('version of python to build virtualenv with '
                              '(default is python2.7)'))

    parser.add_argument('--requirement', '-r',
                        dest='requirements',
                        action='append',
                        default=None,
                        help=('pip requirements file to read, multiple '
                              'allowed (default is empty)'))

    parser.add_argument('--package', '-p',
                        dest='packages',
                        action='append',
                        default=None,
                        help=('pip package index options, multiple '
                              'allowed (default is empty)'))

    parser.add_argument('--output', '-o',
                        dest='output',
                        default=None,
                        help=('name of output zip file (default is '
                              'py-lambda-packer.zip)'))

    parser.add_argument('--archive-dir',
                        dest='archive_dir',
                        default=None,
                        help=('directory to build the archive in '
                              '(default is a tmp dir)'))

    parser.add_argument('--keep-archive',
                        dest='keep_archive',
                        default=None,
                        action='store_true',
                        help=('do not delete archive build directory when '
                              'set (default=False)'))

    parser.add_argument('--generate-config',
                        dest='generate_config',
                        action='store_true',
                        help=('prints thedefault configuration to help create '
                              'one'))

    namespace = parser.parse_args(*argv)
    LOGGER.debug('Command line arguments: %s', namespace)
    return namespace


def entry_point():
    # Only here to be quiet and dump out the config.  Have to do this before
    # activating logging.
    if '--generate-config' in sys.argv[1:]:
        Configuration.print_default_config()
        sys.exit(0)

    # General configuration
    setup_logging()
    cli_args = parse_args(sys.argv[1:])
    config = Configuration(vars(cli_args))
    cwd = os.getcwd()

    # Information for the VirtualEnv
    pip_requirements = config.data['virtualenv']['pip']['requirements']
    fileset_excludes = config.data['virtualenv']['default_excludes']

    # Information for the PyLambdaPacker
    filesets = []
    if config.data['packager']['includes']:
        filesets = [
            FileSet(cwd,
                    includes=config.data['packager']['includes'],
                    excludes=config.data['packager']['excludes']
                    + config.data['packager']['default_excludes'])]

    # Build!
    with VirtualEnv(python=config.data['virtualenv']['python'],
                    path=config.data['virtualenv']['path'],
                    keep=config.data['virtualenv']['keep'],
                    packages=config.data['virtualenv']['pip']['packages'],
                    requirements=pip_requirements,
                    fileset_excludes=fileset_excludes) as virtual_env, \
            Packager(
                zip_file=config.data['packager']['target'],
                build_path=config.data['packager']['build_path'],
                keep=config.data['packager']['keep']) as packager:

        packer = PyLambdaPacker(virtual_env, packager, filesets)
        packer.build()
