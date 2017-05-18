from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import logging


LOGGER = logging.getLogger(__name__)


def expand_path(path, log=False):
    expanded = os.path.normpath(os.path.abspath(path))
    if log and expanded != path:
        LOGGER.debug('Expanded "%s" to "%s".', path, expanded)
    return expanded
