from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from unittest import mock
    from unittest.mock import patch
except ImportError:
    import mock
    from mock import patch

import pytest

from plpacker.fileset import FileSet


class TestFileSetConstructor(object):
    def test_none_directory(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        with pytest.raises(ValueError) as info:
            FileSet(None, ['**'])
        assert str(info.value) == \
            '"None" is not an acceptable "directory" value.'

    def test_blank_directory(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        fileset = FileSet('', ['**'])
        assert fileset.directory == '/'

    def test_none_includes(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        with pytest.raises(ValueError) as info:
            FileSet('', None)
        assert str(info.value) == '"includes" must be provided.'

    def test_scalar_includes(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        fileset = FileSet('', '**')
        assert fileset.includes == ('**',)

    def test_array_includes(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        fileset = FileSet('', ['**'])
        assert fileset.includes == ('**',)

    def test_scalar_excludes(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        fileset = FileSet('', '**', '*.html')
        assert fileset.excludes == ('*.html',)

    def test_array_excludes(self, source_fs):
        # pylint: disable=unused-argument, no-self-use
        fileset = FileSet('', '**', ['*.html'])
        assert fileset.excludes == ('*.html',)

    def test_sane_defaults(self, fileset):
        # pylint: disable=unused-argument, no-self-use
        assert fileset.directory == '/home/foo/src/bar-project'
        assert fileset.includes == ('**',)
        assert fileset.excludes == ('py-lambda-packer.yaml', '**/*.png',
                                    '**/*.html', '**/config.*')
        assert fileset.followlinks
        assert fileset.fileset == (
            '.git/config',
            '.gitignore',
            'posts/a/b/c/d/tess.txt',
            'static/images/large.gif',
            'static/images/large.jpg')

    @patch.object(FileSet, '_expand_fileset')
    def test_calls_expand_fileset(self, expand_fileset_mock, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        expand_fileset_mock.return_value = ()
        FileSet('/home/foo/src/bar-project',
                includes=['**'],
                excludes=['c*i.jpg'],
                followlinks=True)
        expand_fileset_mock.assert_called_with()
        assert expand_fileset_mock.call_count == 1


class TestFileSetExpandFileset(object):
    def test_end_to_end(self, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        assert fileset._expand_fileset() == (
            '.git/config',
            '.gitignore',
            'posts/a/b/c/d/tess.txt',
            'static/images/large.gif',
            'static/images/large.jpg')

    def test_include_exclude_all(self, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        fileset = FileSet('/home/foo/src/bar-project', ['**'], ['**'])
        actual = fileset._expand_fileset()
        assert actual == ()

    @patch.object(FileSet, '_expand_glob')
    def test_calls_expand_glob(self, expand_glob_mock, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        expand_glob_mock.return_value = []
        FileSet('/home/foo/src/bar-project',
                includes=['**'],
                excludes=['c*i.jpg'],
                followlinks=True)
        expand_glob_mock.assert_has_calls([mock.call('**', True),
                                           mock.call('c*i.jpg', True)])
        assert expand_glob_mock.call_count == 2


class TestFileSetExpandGlob(object):
    good_expressions = (
        # Nothing returns nothing
        ('',
         ()),
        # Directory with multiple directories, but a single file.
        ('*',
         ('config.json', 'py-lambda-packer.yaml')),
        # Dot '.*' file'
        ('.*',
         ('.gitignore',)),
        # Single include glob, multiple files retured
        ('static/images/*',
         ('static/images/hello.png',
          'static/images/large.gif',
          'static/images/large.jpg',
          'static/images/large.png',
          'static/images/thumb.png')),
        # More complex, single include glob, multiple files retured
        ('static/images/*.png',
         ('static/images/hello.png',
          'static/images/large.png',
          'static/images/thumb.png')),
        # Splat in the middle
        ('*/images/*.png',
         ('static/images/hello.png',
          'static/images/large.png',
          'static/images/thumb.png',
          'templates/images/index.png')),
        # Recursive with splat in the middle
        ('posts/*/b/**/*.html',
         ('posts/a/b/c/d/bw.html',
          'posts/a/b/c/d/e/bar.html',
          'posts/a/b/c/d/e/got.html',
          'posts/a/b/c/d/tess.html',
          'posts/a1/b/diff/bw.html')),
    )

    @pytest.mark.parametrize("expression,expected", good_expressions)
    def test_skip_directories(self, expression, expected, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        actual = fileset._expand_glob(expression)
        assert actual == expected

    absolute_paths = (
        # Do not return directories.
        '/DOES_NOT_EXIST_987987/*',
        # Do not return directories.
        '/home/*',
        # Trailing slash in directory include glob
        '/home/',
        # No trailing slash
        '/home',
    )

    @pytest.mark.parametrize("expression", absolute_paths)
    def test_absolute_paths(self, expression, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        with pytest.raises(ValueError) as info:
            fileset._expand_glob(expression)
        assert str(info.value) == \
            'Absolute paths in globs are not supported: {}'.format(expression)

    relative_paths = (
        # Reletive paths work
        '../config/global-config.json',
        # More reletive paths
        './*.json',
        # Overkilled reletive paths work
        '../config/./global-config.json',
    )

    @pytest.mark.parametrize("expression", relative_paths)
    def test_relative_paths(self, expression, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        with pytest.raises(ValueError) as info:
            fileset._expand_glob(expression)
        assert str(info.value) == \
            'Dots (".." or ".") are not permitted: {}'.format(expression)

    double_splat = (
        ('posts/a/b/c/**',
         ('posts/a/b/c/d/bw.html',
          'posts/a/b/c/d/e/bar.html',
          'posts/a/b/c/d/e/got.html',
          'posts/a/b/c/d/tess.html',
          'posts/a/b/c/d/tess.txt')),
        ('posts/a/**/*.html',
         ('posts/a/b/c/d/bw.html',
          'posts/a/b/c/d/e/bar.html',
          'posts/a/b/c/d/e/got.html',
          'posts/a/b/c/d/tess.html',
          'posts/a/ref-90.html')),
        ('posts/a/**/e/*.html', ()),
        ('posts/a/**/c/**/e/*.html', ()),
    )

    @pytest.mark.parametrize("expression,expected", double_splat)
    def test_recursive_without_symlinks(self, expression, expected, fileset,
                                        source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        actual = fileset._expand_glob(expression)
        assert actual == expected

    def test_root_double_splat(self, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        actual = fileset._expand_glob('**')
        assert len(actual) == 21

    def test_root_double_splat_followlinks(self, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use
        # pylint: disable=invalid-name,protected-access
        actual = fileset._expand_glob('**', followlinks=True)
        assert len(actual) == 23

    def test_recursive_follow_symlinks(self, fileset, source_fs):
        # pylint: disable=unused-argument,no-self-use,protected-access
        actual = fileset._expand_glob(
            'posts/a/b/c/**/*.html',
            followlinks=True)
        assert actual == (
            'posts/a/b/c/d/bw.html',
            'posts/a/b/c/d/e/bar.html',
            'posts/a/b/c/d/e/got.html',
            'posts/a/b/c/d/symlink-dir/link-00.html',
            'posts/a/b/c/d/symlink-dir/link-03.html',
            'posts/a/b/c/d/tess.html')


class TestIterator(object):
    def test_len(self, fileset):
        # pylint: disable=no-self-use
        assert len(fileset) == 5

    def test_getitem(self, fileset):
        # pylint: disable=no-self-use
        assert fileset[0] == '.git/config'
        assert fileset[1] == '.gitignore'
        assert fileset[2] == 'posts/a/b/c/d/tess.txt'
        assert fileset[3] == 'static/images/large.gif'
        assert fileset[4] == 'static/images/large.jpg'

    def test_iterator(self, fileset):
        # pylint: disable=no-self-use
        iterator = iter(fileset)
        assert next(iterator) == '.git/config'
        assert next(iterator) == '.gitignore'
        assert next(iterator) == 'posts/a/b/c/d/tess.txt'
        assert next(iterator) == 'static/images/large.gif'
        assert next(iterator) == 'static/images/large.jpg'

    def test_pairs_iterator(self, fileset):
        # pylint: disable=no-self-use
        iterator = fileset.pairs()
        assert next(iterator) == (
            '/home/foo/src/bar-project/.git/config',
            '.git/config')
        assert next(iterator) == (
            '/home/foo/src/bar-project/.gitignore',
            '.gitignore')
        assert next(iterator) == (
            '/home/foo/src/bar-project/posts/a/b/c/d/tess.txt',
            'posts/a/b/c/d/tess.txt')
        assert next(iterator) == (
            '/home/foo/src/bar-project/static/images/large.gif',
            'static/images/large.gif')
        assert next(iterator) == (
            '/home/foo/src/bar-project/static/images/large.jpg',
            'static/images/large.jpg')
