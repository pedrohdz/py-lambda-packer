from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import logging.config


LOGGER = logging.getLogger()


class PyLambdaPacker(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, virtual_env, packager, filesets):
        super(PyLambdaPacker, self).__init__()
        self.virtual_env = virtual_env
        self.packager = packager
        self.filesets = filesets

    def build(self):
        # Create virtualenv
        self.virtual_env.create()
        filesets = []
        if self.filesets:
            filesets += self.filesets
        if self.virtual_env.filesets:
            filesets += self.virtual_env.filesets

        for fileset in filesets:
            self.packager.add_fileset_items(fileset)
        self.packager.package()
