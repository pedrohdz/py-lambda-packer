#!/usr/bin/env python
import re
import sys
import ast
from setuptools import setup, find_packages

_ENTRY_POINT = 'plpacker.cli:entry_point'


def version():
    version_re = re.compile(r'__version__\s+=\s+(.*)')
    with open('plpacker/__init__.py', 'rb') as handle:
        return str(ast.literal_eval(version_re.search(
            handle.read().decode('utf-8')).group(1)))


def long_description():
    with open('README.rst', 'rb') as handle:
        return handle.read().decode('utf-8')


_TEST_REQUIRE = [
    'pyfakefs>=3.5',
    'pytest-cov>=2.5.1',
    'pytest>=3.0.7',
]

if sys.version_info[0] < 3:
    _TEST_REQUIRE.extend(['mock'])

_CI_REQUIRE = [
    'coverage>=4.4.1',
    'flake8>=3.3.0',
    'pep257>=0.7.0',
    'pylint>=1.7.1',
    'tox>=2.7.0',
]

setup(
    name='py-lambda-packer',
    version=version(),
    author='Pedro H.',
    author_email='pedro@digitalrounin.com',
    description='Helps build AWS Lambda zip files for Python projects.',
    long_description=long_description(),
    url='https://github.com/digitalrounin/py-lambda-packer.git',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='aws lambda',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    setup_requires=[
        'pytest-runner',
    ],
    install_requires=[
        'PyYAML>=3.12',
        'colorlog>=2.10.0',
        'future>=0.16.0',
    ],
    tests_require=_TEST_REQUIRE,
    extras_require={
        'ci': _CI_REQUIRE,
        'test': _TEST_REQUIRE,
    },
    entry_points={'console_scripts': [
        'py-lambda-packer = {}'.format(_ENTRY_POINT),
        'plp = {}'.format(_ENTRY_POINT),
    ]},
)
