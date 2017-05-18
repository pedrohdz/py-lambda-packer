from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import fnmatch
from glob import glob
import os
import logging

import plpacker.utils

LOGGER = logging.getLogger(__name__)


class FileSet(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, directory, includes, excludes=(), followlinks=False):
        # Validate
        if directory is None:
            raise ValueError('"None" is not an acceptable "directory" value.')
        if not includes:
            raise ValueError('"includes" must be provided.')

        # Scalars to tuples
        if not isinstance(includes, (list, tuple)):
            includes = (includes,)
        if excludes and not isinstance(excludes, (list, tuple)):
            excludes = (excludes,)

        # Save
        self.directory = plpacker.utils.expand_path(directory, True)
        self.includes = (includes
                         if isinstance(includes, tuple) else tuple(includes))
        self.excludes = (excludes
                         if isinstance(excludes, tuple) else tuple(excludes))
        self.followlinks = followlinks
        self.fileset = self._expand_fileset()

    def __len__(self):
        return len(self.fileset)

    def __getitem__(self, index):
        return self.fileset[index]

    def __iter__(self):
        return iter(self.fileset)

    def pairs(self):
        return ((os.path.join(self.directory, item),
                 item) for item in self.fileset)

    def _expand_fileset(self):
        files = set()
        for include in self.includes:
            files.update(self._expand_glob(include, self.followlinks))

        for exclude in self.excludes:
            files = files.difference(
                self._expand_glob(exclude, self.followlinks))

        return tuple(sorted(item for item in files))

    def _expand_glob(self, expression, followlinks=False):
        if os.path.isabs(expression):
            raise ValueError('Absolute paths in globs are not supported: {}'
                             .format(expression))

        if expression:
            full_glob = os.path.join(self.directory, expression)
        else:
            full_glob = self.directory

        if full_glob != os.path.normpath(full_glob):
            raise ValueError('Dots (".." or ".") are not permitted: {}'
                             .format(expression))

        if '**' in expression:
            result = _find_files_recursively(full_glob, followlinks)
        else:
            result = _find_files(full_glob)
        directory_len = len(self.directory) + 1
        return tuple(sorted(item[directory_len:] for item in result))


def _find_files_recursively(expression, followlinks=False):
    if '**' not in expression:
        raise ValueError('Glob is missing "**": {}'.format(expression))
    (directories, glob_part) = expression.rsplit('**', 1)
    if not glob_part:
        glob_part = '*'
    elif glob_part.startswith(os.path.sep):
        glob_part = glob_part[len(os.path.sep):]

    result = []
    for directory in glob(directories):
        for (dirpath, _, filenames) in os.walk(
                directory, followlinks=followlinks):
            for filename in fnmatch.filter(filenames, glob_part):
                result.append(os.path.join(dirpath, filename))
    return result


def _find_files(expression):
    items = []
    for item in glob(expression):
        if os.path.isfile(item):
            items.append(item)
    return items
