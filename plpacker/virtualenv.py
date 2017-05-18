from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os
import logging
import platform
import shutil
import subprocess
import tempfile

from plpacker.fileset import FileSet
from plpacker.utils import expand_path

LOGGER = logging.getLogger(__name__)


class VirtualEnv(object):
    def __init__(self, python=None, path=None, keep=None, packages=None,
                 requirements=None, fileset_excludes=None):
        # pylint: disable=too-many-arguments
        self.python = python
        self.keep = keep
        self.packages = packages
        self.requirements = requirements
        self.fileset_excludes = fileset_excludes

        if not path:
            prefix = '{}-'.format(__name__)
            self.path = tempfile.mkdtemp(suffix='-tmp', prefix=prefix)
        else:
            self.path = expand_path(path, True)
            os.mkdir(self.path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # pylint: disable=unused-variable
        try:
            self.clean()
        except RuntimeError as exception:  # noqa
            # `exception` is a stupid hack to avoid pylint dub code errors with
            # packager.Packager.
            pass
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Failed to clean up virtual environment.')

    def create(self):
        command = ['virtualenv']
        if self.python:
            command += ['--python', self.python]
        command += [self.path]

        LOGGER.info('Creating virtualenv in: %s', self.path)
        self.run(command, cwd=self.path)

        if self.packages or self.requirements:
            self.install(self.packages, self.requirements)

    def install(self, packages=(), requirements=()):
        if not (packages or requirements):
            raise RuntimeError(
                'Either, or both, "packages" or "requirements" must be '
                'provided.')
        req_args = []
        for item in requirements:
            req_args += ['-r', item]
        self.run([self.pip_exec(), 'install'] + req_args + list(packages))

    def pip_exec(self):
        if platform.system() == 'Windows':
            return os.path.join(self.path, 'Scripts', 'pip.exe')
        return os.path.join(self.path, 'bin', 'pip')

    def run(self, args, cwd=None):
        LOGGER.info('Executing command "%s".', ' '.join(args))
        process = subprocess.Popen(args,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   env=self.sanitized_env(),
                                   cwd=cwd)
        (stdoutdata, stderrdata) = process.communicate()
        if stdoutdata:
            LOGGER.debug(stdoutdata)
        if stderrdata:
            LOGGER.error(stderrdata)
        if process.returncode != 0:
            raise RuntimeError('Command failed: "{}"'.format(' '.join(args)))

    @property
    def site_package_dirs(self):
        dirs = os.path.join(self.path, 'lib', '*', 'site-packages')
        return glob.glob(dirs)

    @property
    def filesets(self):
        sets = []
        for directory in self.site_package_dirs:
            fileset = FileSet(directory, includes='**',
                              excludes=self.fileset_excludes)
            sets.append(fileset)
        return sets

    def clean(self):
        if not (self.path and os.path.isdir(self.path)):
            raise RuntimeError(
                'Virtualenv was never created, nothing to clean.')

        if not self.keep:
            LOGGER.info('Deleting virtualenv in: %s', self.path)
            shutil.rmtree(self.path)
        else:
            LOGGER.warning('Virtualenv directory marked for keeping: %s',
                           self.path)

    @staticmethod
    def sanitized_env():
        env = dict(os.environ)
        if 'VIRTUAL_ENV' in env:
            virtual_env = env['VIRTUAL_ENV']
            env['PATH'] = ':'.join([item for item in env['PATH'].split(':')
                                    if not item.startswith(virtual_env)])
            del env['VIRTUAL_ENV']
        if '__PYVENV_LAUNCHER__' in env:
            del env['__PYVENV_LAUNCHER__']
        return env
