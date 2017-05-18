from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import shutil
import tempfile
import logging
from zipfile import ZipFile, ZIP_DEFLATED

from plpacker.utils import expand_path

LOGGER = logging.getLogger(__name__)


class Packager(object):
    def __init__(self, zip_file, build_path=None, keep=False):
        self.zip_file = expand_path(zip_file, True)
        self.keep = keep

        if not build_path:
            prefix = '{}-'.format(__name__)
            self.build_path = tempfile.mkdtemp(suffix='-zip', prefix=prefix)
        else:
            self.build_path = expand_path(build_path, True)
            os.mkdir(self.build_path)
        LOGGER.debug('Staging files to zip in: %s', self.build_path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.clean()
        except RuntimeError:
            pass
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Failed to clean up staging directory.')

    def __enter__(self):
        return self

    def add_fileset_items(self, fileset):
        for (source, target) in fileset.pairs():
            target = os.path.join(self.build_path, target)
            target_dir = os.path.dirname(target)
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)
            LOGGER.debug('Copying "%s" to "%s".', source, target)
            shutil.copyfile(source, target)

    def package(self):
        LOGGER.info('Packaging files to "%s".', self.zip_file)
        build_path_len = len(self.build_path) + 1
        archive = ZipFile(self.zip_file, 'w', ZIP_DEFLATED)
        try:
            for (dirpath, _, filenames) in os.walk(self.build_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    arcname = file_path[build_path_len:]
                    archive.write(file_path, arcname)
        finally:
            archive.close()

    def clean(self):
        if not (self.build_path and os.path.isdir(self.build_path)):
            raise RuntimeError(
                'Package staging directory was never created, nothing '
                'to clean.')

        if not self.keep:
            LOGGER.info('Deleting package staging directory: %s',
                        self.build_path)
            shutil.rmtree(self.build_path)
        else:
            LOGGER.warning('Package directory marked for keeping: %s',
                           self.build_path)
