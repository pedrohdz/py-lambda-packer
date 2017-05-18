from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import zipfile

import pytest

from plpacker.packager import Packager


class TestConstructor(object):
    def test_sane_defaults(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        packer = Packager('zip.zip')
        assert not packer.keep
        # pylint: disable=len-as-condition
        assert len(packer.build_path) > 0
        assert os.path.isabs(packer.build_path)

    def test_with(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        with Packager('zip.zip') as packer:
            assert os.path.exists(packer.build_path)
        assert not os.path.exists(packer.build_path)

    def test_creates_build_dir(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        build_path = '/home/foo/tmp/build'
        packer = Packager('zip.zip', build_path)
        assert os.path.exists(packer.build_path)

    def test_error_on_existing_build_dir(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        # pylint: disable=invalid-name
        build_path = '/home/foo/tmp'
        with pytest.raises(OSError):
            Packager('zip.zip', build_path)


class TestClean(object):
    def test_deletes_build_dir(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        build_path = '/home/foo/tmp/build'
        packer = Packager('zip.zip', build_path)
        packer.package()
        packer.clean()
        assert not os.path.exists(build_path)

    def test_keeps(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        build_path = '/home/foo/tmp/build'
        packer = Packager('zip.zip', build_path, True)
        packer.package()
        packer.clean()
        assert os.path.exists(build_path)

    def test_uses_default_dir(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        packer = Packager('zip.zip', keep=True)
        packer.package()
        packer.clean()
        assert os.path.exists(packer.build_path)


class TestPackage(object):
    target_paths = (
        ('/home/foo/src/bar-project',
         'foo.zip',
         '/home/foo/src/bar-project/foo.zip'),
        ('/home/foo/src/bar-project',
         'bar.zip',
         '/home/foo/src/bar-project/bar.zip'),
        ('/home/foo/tmp',
         'loohoo.zip',
         '/home/foo/tmp/loohoo.zip'),
        ('/home/foo/src/bar-project',
         '/home/foo/tmp/ha.zip',
         '/home/foo/tmp/ha.zip'),
    )

    @pytest.mark.parametrize("cwd,target,expected", target_paths)
    def test_zip_target_locations(self, cwd, target, expected, source_fs,
                                  fileset):
        # pylint: disable=unused-argument,no-self-use,too-many-arguments
        os.chdir(cwd)
        packager = Packager(zip_file=target)
        packager.add_fileset_items(fileset)
        packager.package()
        assert os.path.exists(expected)
        assert os.path.isfile(expected)

    def test_zip_is_healthy(self, packager, source_fs, fileset):
        # pylint: disable=unused-argument, no-self-use
        packager.add_fileset_items(fileset)
        packager.package()

        zip_path = os.path.join('/home/foo/src/bar-project', 'zip.zip')
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            assert not zip_file.testzip()

    def test_zip_contents(self, packager, source_fs, fileset):
        # pylint: disable=unused-argument, no-self-use
        packager.add_fileset_items(fileset)
        packager.package()

        zip_path = os.path.join('/home/foo/src/bar-project', 'zip.zip')
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            contents = zip_file.namelist()
            contents.sort()

        assert contents == ['.git/config',
                            '.gitignore',
                            'posts/a/b/c/d/tess.txt',
                            'static/images/large.gif',
                            'static/images/large.jpg']
