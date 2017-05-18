from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def log(logger):
    """
    Example:
        import plpacker
        import tests.helpers
        tests.helpers.log(plpacker.packager.LOGGER)
    """
    import logging

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
