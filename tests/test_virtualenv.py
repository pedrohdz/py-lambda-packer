from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str  # noqa pylint: disable=redefined-builtin

import os
import re

try:
    from unittest.mock import patch, sentinel
except ImportError:
    from mock import patch, sentinel

import pytest

from plpacker.virtualenv import VirtualEnv


class TestVirtualEnvConstructor(object):
    def test_sane_defaults(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        venv = VirtualEnv()
        assert not venv.keep
        # pylint: disable=len-as-condition
        assert len(venv.path) > 0
        assert os.path.isabs(venv.path)

    def test_with(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        with VirtualEnv() as venv:
            # import pdb ; pdb.set_trace()
            assert os.path.exists(venv.path)
        assert not os.path.exists(venv.path)

    def test_exception_on_existing_build_path(self, source_fs):
        # pylint: disable=unused-argument,invalid-name,no-self-use
        build_path = '/home/foo/tmp'
        with pytest.raises(OSError):
            VirtualEnv(path=build_path)

    def test_creates_build_dir(self, source_fs):
        # pylint: disable=unused-argument,no-self-use
        build_path = '/home/foo/tmp/build'
        VirtualEnv(path=build_path)
        assert os.path.exists(build_path)


class TestVirtualEnvCreate(object):
    @patch.object(VirtualEnv, 'run')
    def test_defaults(self, run_mock, source_fs, virtual_env):
        # pylint: disable=unused-argument,no-self-use
        virtual_env = VirtualEnv()
        virtual_env.create()
        run_mock.assert_called_once()

        regex = re.compile(r'^\/.*\/plpacker\.virtualenv-\w+-tmp$')
        (call_args, call_kargs) = run_mock.call_args

        assert call_args[0][0] == 'virtualenv'
        assert regex.match(call_args[0][1])
        assert regex.match(call_kargs['cwd'])

    @patch.object(VirtualEnv, 'run')
    def test_with_python(self, run_mock, source_fs):
        # pylint: disable=unused-argument,no-self-use
        venv = VirtualEnv(python=sentinel.python)
        venv.create()
        run_mock.assert_called_once()

        regex = re.compile(r'^\/.*\/plpacker\.virtualenv-\w+-tmp$')
        (call_args, call_kargs) = run_mock.call_args

        assert call_args[0][0] == 'virtualenv'
        assert call_args[0][1] == '--python'
        assert call_args[0][2] == sentinel.python
        assert regex.match(call_args[0][3])
        assert regex.match(call_kargs['cwd'])

    @patch.object(VirtualEnv, 'run')
    def test_with_target_path(self, run_mock, source_fs):
        # pylint: disable=unused-argument,invalid-name,no-self-use
        build_path = '/home/foo/tmp/venv-TPTka'
        venv = VirtualEnv(path=build_path)
        venv.create()
        run_mock.assert_called_once()

        (call_args, call_kargs) = run_mock.call_args

        assert call_args[0][0] == 'virtualenv'
        assert call_args[0][1] == build_path
        assert call_kargs['cwd'] == build_path


class TestVirtualEnvInstall(object):
    def test_packages_or_reqs(self, source_fs, virtual_env):
        # pylint: disable=unused-argument,no-self-use
        with pytest.raises(RuntimeError) as info:
            virtual_env.install()
        assert ('Either, or both, "packages" or "requirements" must be '
                'provided.') in str(info.value)

    @patch.object(VirtualEnv, 'run')
    def test_calls_pip_packages_and_reqs_full(self, run_mock, source_fs):
        # pylint: disable=unused-argument,no-self-use,invalid-name
        build_path = '/home/foo/tmp/venv-K7aC6'
        venv = VirtualEnv(path=build_path)
        venv.install(packages=['pytest', 'pip', 'Flask'],
                     requirements=['requirements.txt',
                                   'requirements-dev.txt'])

        run_mock.assert_called_once()
        call_args = run_mock.call_args[0]

        pip_path = os.path.join(build_path, 'bin', 'pip')
        assert call_args[0] == [pip_path, 'install',
                                '-r', 'requirements.txt',
                                '-r', 'requirements-dev.txt',
                                'pytest', 'pip', 'Flask']

    @patch.object(VirtualEnv, 'run')
    def test_calls_pip_with_packages(self, run_mock, source_fs):
        # pylint: disable=unused-argument,no-self-use
        build_path = '/home/foo/tmp/venv-si6aJ'
        venv = VirtualEnv(path=build_path)
        venv.install(packages=['pytest', 'pip', 'Flask'])

        call_args = run_mock.call_args[0]

        pip_path = os.path.join(build_path, 'bin', 'pip')
        assert call_args[0] == [pip_path, 'install',
                                'pytest', 'pip', 'Flask']

    @patch.object(VirtualEnv, 'run')
    def test_calls_pip_with_requirements(self, run_mock, source_fs):
        # pylint: disable=unused-argument,invalid-name,no-self-use
        build_path = '/home/foo/tmp/venv-K7aC6'
        venv = VirtualEnv(path=build_path)
        venv.install(requirements=['requirements.txt',
                                   'requirements-dev.txt'])

        call_args = run_mock.call_args[0]

        pip_path = os.path.join(build_path, 'bin', 'pip')
        assert call_args[0] == [pip_path, 'install',
                                '-r', 'requirements.txt',
                                '-r', 'requirements-dev.txt']


class TestVirtualEnvRun(object):
    @staticmethod
    def config_popen_mock(popen):
        instance = popen.return_value
        instance.communicate.return_value = (None, None)
        instance.returncode = 0
        return instance

    @patch('subprocess.Popen')
    def test_full_call(self, popen, virtual_env):
        instance = self.config_popen_mock(popen)
        fake_cwd = '/QcN55kaQ0D/v1wygcumsc/Hp9Oy4KT5q'

        virtual_env.run(['qfjzN2hzXX', 'kre1st5tgX'], cwd=fake_cwd)

        instance.communicate.assert_called_once()
        (call_args, call_kargs) = popen.call_args
        assert call_args == (['qfjzN2hzXX', 'kre1st5tgX'],)
        assert call_kargs['cwd'] == fake_cwd
        assert call_kargs['env']

    @patch.object(VirtualEnv, 'sanitized_env')
    @patch('subprocess.Popen')
    def test_calls_sanitized_env(self, popen, sanitized_env, virtual_env):
        self.config_popen_mock(popen)
        sanitized_env.return_value = sentinel.sanitized_env
        virtual_env.run(['5VgqesWb5u'])

        sanitized_env.assert_called_once()

        # Popen was created with env from sanitized_env.
        call_kargs = popen.call_args[1]
        assert call_kargs['env'] == sentinel.sanitized_env

    @pytest.mark.parametrize("return_code", [-653874, -1, 1, 23498])
    @patch('subprocess.Popen')
    def test_fails_on_non_zero_ret_code(self, popen, virtual_env, return_code):
        # pylint: disable=no-self-use
        instance = popen.return_value
        instance.communicate.return_value = (None, None)
        instance.returncode = return_code

        with pytest.raises(RuntimeError) as info:
            virtual_env.run(['W4lO7tPBtM'])
        assert 'Command failed: "W4lO7tPBtM"' in str(info.value)


class TestVirtualEnvSanitizedEnv(object):
    def test_deletes_env_vars(self, virtual_env):
        # pylint: disable=no-self-use
        values = {
            'VIRTUAL_ENV': 'SOME_VALUE_HERE',
            '__PYVENV_LAUNCHER__': 'SOME_OTHER_VALUE_HERE',
            'PATH': '/SOME/PATH/HERE',
            'uhaXJf': 'aFAx8t'
        }
        with patch.dict('os.environ', values=values, clear=True):
            env = virtual_env.sanitized_env()

        assert env == {'PATH': '/SOME/PATH/HERE', 'uhaXJf': 'aFAx8t'}
        # Redundant...  But explicite...
        assert 'VIRTUAL_ENV' not in env
        assert '__PYVENV_LAUNCHER__' not in env

    def test_trims_path(self, virtual_env):
        # pylint: disable=no-self-use
        venv_path = '/Y1w4sD/DELETE/THIS/ISUy0r'
        values = {
            'VIRTUAL_ENV': venv_path,
            'PATH': ':'.join(('/0ho8Ke/hL9DsW/ymH81W',
                              '/L51pua',
                              '/Vngp3V/G2m7Ih/05m7qW/LyrYkK/l5NuwA/oq1DPp',
                              venv_path,
                              '/Zpdhu4/bjvuqt',
                              '/STGtcb/FhAnWH/HwTvOr/gngGiB',
                              '/Zizj4D/szncsv/O5wO6X/joFHVT'))
        }
        with patch.dict('os.environ', values=values, clear=True):
            env = virtual_env.sanitized_env()

        assert venv_path not in env['PATH']
        assert env['PATH'] == (
            '/0ho8Ke/hL9DsW/ymH81W:/L51pua:/Vngp3V/G2m7Ih/05m7qW/LyrYkK/'
            'l5NuwA/oq1DPp:/Zpdhu4/bjvuqt:/STGtcb/FhAnWH/HwTvOr/gngGiB:'
            '/Zizj4D/szncsv/O5wO6X/joFHVT')
