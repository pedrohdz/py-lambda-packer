from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import pytest
from pyfakefs.fake_filesystem_unittest import Patcher

from plpacker.packager import Packager
from plpacker.virtualenv import VirtualEnv
from plpacker.fileset import FileSet


# -----------------------------------------------------------------------------
# Global fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope='function')
def source_fs(request):
    patcher = Patcher()
    patcher.setUp()
    request.addfinalizer(patcher.tearDown)

    patcher.fs.CreateFile('/home/foo/src/bar-project/config.json')
    patcher.fs.CreateFile('/home/foo/src/bar-project/.gitignore')
    patcher.fs.CreateFile('/home/foo/src/bar-project/.git/config')
    patcher.fs.CreateFile('/home/foo/src/bar-project/py-lambda-packer.yaml')
    patcher.fs.CreateFile('/home/foo/src/bar-project/templates/images/index.png')  # noqa
    patcher.fs.CreateFile('/home/foo/src/bar-project/templates/index.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/static/images/hello.png')
    patcher.fs.CreateFile('/home/foo/src/bar-project/static/images/thumb.png')
    patcher.fs.CreateFile('/home/foo/src/bar-project/static/images/large.png')
    patcher.fs.CreateFile('/home/foo/src/bar-project/static/images/large.jpg')
    patcher.fs.CreateFile('/home/foo/src/bar-project/static/images/large.gif')
    patcher.fs.CreateDirectory('/home/foo/src/bar-project/static/css')
    patcher.fs.CreateDirectory('/home/foo/src/bar-project/static/js')
    patcher.fs.CreateFile('/home/foo/src/config/global-config.json')

    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/b/c/d/bw.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a1/b/diff/bw.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/b/c/d/e/bar.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/b/c/d/e/got.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/b/c/d/tess.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/b/c/d/tess.txt')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/a/ref-90.html')
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/bucket/link-00.html')  # noqa
    patcher.fs.CreateFile('/home/foo/src/bar-project/posts/bucket/link-03.html')  # noqa

    patcher.fs.CreateLink(
        '/home/foo/src/bar-project/posts/a/b/c/d/symlink-dir',
        '/home/foo/src/bar-project/posts/bucket')
    patcher.fs.CreateLink(
        '/home/foo/src/bar-project/posts/links/tef-90.html',
        '/home/foo/src/bar-project/posts/a/b/dpo.html')

    patcher.fs.CreateDirectory('/home/foo/tmp')

    return patcher.fs


@pytest.fixture(scope='function')
def fileset(source_fs):
    # pylint: disable=unused-argument,redefined-outer-name
    os.chdir('/home/foo/src/bar-project')
    return FileSet('/home/foo/src/bar-project',
                   includes=['**'],
                   excludes=['py-lambda-packer.yaml',
                             '**/*.png',
                             '**/*.html',
                             '**/config.*'],
                   followlinks=True)


@pytest.fixture(scope='function')
def packager(source_fs):
    # pylint: disable=unused-argument,redefined-outer-name
    os.chdir('/home/foo/src/bar-project')
    return Packager('zip.zip')


@pytest.fixture(scope='function')
def virtual_env(source_fs):
    # pylint: disable=unused-argument,redefined-outer-name
    return VirtualEnv()
