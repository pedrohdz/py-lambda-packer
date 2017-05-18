from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from unittest.mock import patch, sentinel, call
except ImportError:
    from mock import patch, sentinel, call

from plpacker.pylambdapacker import PyLambdaPacker


class TestPyLambdaPackerConstuctor(object):
    # pylint: disable=too-few-public-methods
    def test_properties_set(self):
        # pylint: disable=no-self-use
        packer = PyLambdaPacker(
            virtual_env=sentinel.virtual_env,
            packager=sentinel.packager,
            filesets=sentinel.filesets)
        assert packer.virtual_env == sentinel.virtual_env
        assert packer.packager == sentinel.packager
        assert packer.filesets == sentinel.filesets


class TestPyLambdaPackerBuild(object):
    # pylint: disable=too-few-public-methods
    @patch('plpacker.packager.Packager')
    @patch('plpacker.virtualenv.VirtualEnv')
    def test_foo(self, virtual_env, packager):
        # pylint: disable=no-self-use
        virtual_env.filesets = (sentinel.venv_fileset1,
                                sentinel.venv_fileset2)
        filesets = (sentinel.fileset1, sentinel.fileset2, sentinel.fileset3)
        packer = PyLambdaPacker(
            virtual_env=virtual_env,
            packager=packager,
            filesets=filesets)

        packer.build()

        virtual_env.create.assert_called_with()
        packager.add_fileset_items.assert_has_calls([
            call(sentinel.fileset1),
            call(sentinel.fileset2),
            call(sentinel.fileset3),
            call(sentinel.venv_fileset1),
            call(sentinel.venv_fileset2)])
        packager.package.assert_called_with()
