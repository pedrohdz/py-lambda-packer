[![Code Climate](https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg)](https://codeclimate.com/github/digitalrounin/py-lambda-packer)
[![Build Status](https://travis-ci.org/digitalrounin/py-lambda-packer.svg?branch=master)](https://travis-ci.org/digitalrounin/py-lambda-packer)
[![codecov](https://codecov.io/gh/digitalrounin/py-lambda-packer/branch/master/graph/badge.svg)](https://codecov.io/gh/digitalrounin/py-lambda-packer)
[![PyPI version](https://badge.fury.io/py/py-lambda-packer.svg)](https://badge.fury.io/py/py-lambda-packer)


# py-lambda-packer

A Python AWS Lambda packager.  This projects is very loosely based on the work
in [serverless-wsgi][].

**NOTICE**: _This project is a work in progress and should be considered
unstable._

Features:

- Written to run under both _Python 3.6_ and _2.7_.
- Generates _Python 3.6_ and _2.7_ _AWS Lambda Deployment Packages_, user
  configurable.
- _AWS Lambda Deployment Packages_ are generated in isolated, temporary
  _virtualenvs_.
- Per project configuration files to cut down on typing.
- Can be easily be included and integrated into other projects as a library.


## Usage

### Installation

#### Latest stable

```
$ pip install py-lambda-packer
```

#### Bleeding edge

To install directly the bleeding edge version from _GitHub_:

```
$ pip install git+https://github.com/digitalrounin/py-lambda-packer.git@master#egg=py-lambda-packer
```

To install a specific tag or branch, replace `master` in the URL of the
previous command with the desired name.


### Quick start

Quick example command to generate `py-lambda-package.zip` for upload to _AWS_
as a _Lambda Function_

```
$ py-lambda-packer --requirement requirements.txt --package . \
    --python python3.6 --include LICENSE
```


### Command help

Command help information:

```
$ py-lambda-packer --help

usage: py-lambda-packer [-h] [--config-file CONFIG_FILE] [--include INCLUDES]
                        [--exclude EXCLUDES] [--followlinks]
                        [--virtualenv-dir VIRTUALENV_DIR] [--keep-virtualenv]
                        [--python PYTHON] [--requirement REQUIREMENTS]
                        [--package PACKAGES] [--output OUTPUT]
                        [--archive-dir ARCHIVE_DIR] [--keep-archive]
                        [--generate-config]

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        location of configuration file (default: ./py-lambda-
                        packer.yaml)
  --include INCLUDES    glob pattern of what to include, multiple allowed
                        (default is empty)
  --exclude EXCLUDES    glob pattern of what to exclude, multiple allowed
                        (default is empty)
  --followlinks         follows symbolic links (default=False)
  --virtualenv-dir VIRTUALENV_DIR
                        directory to build the virtualenv in (default is a tmp
                        dir)
  --keep-virtualenv     do not delete virtualenv build directory when set
                        (default=False)
  --python PYTHON       version of python to build virtualenv with (default is
                        python2.7)
  --requirement REQUIREMENTS, -r REQUIREMENTS
                        pip requirements file to read, multiple allowed
                        (default is empty)
  --package PACKAGES, -p PACKAGES
                        pip package index options, multiple allowed (default
                        is empty)
  --output OUTPUT, -o OUTPUT
                        name of output zip file (default is py-lambda-
                        packer.zip)
  --archive-dir ARCHIVE_DIR
                        directory to build the archive in (default is a tmp
                        dir)
  --keep-archive        do not delete archive build directory when set
                        (default=False)
  --generate-config     prints thedefault configuration to help create one

```


### Project configuration

Project configuration file are named `py-lambda-packer.yaml` in the base
directory of your project.  Here is an example:

```
virtualenv:
  python: python2.7
  pip:
    requirements:
      - requirements.txt
    packages:
      - .
      - Flask

packager:
  target: py-lambda-package.zip
  followlinks: true
  includes:
    - LICENSE
    - static/**
    - templates/**/*.html
  excludes:
    - static/**/*.tmp
```

To generate a configuration file, try the `py-lambda-packer --generate-config`
command.


## Todo list

- Bump up code coverage limit back up to 80% and fix failing source files.
- Add comments to configuration file created by `py-lambda-packer
  --generate-config`.
- Document the _py-lambda-packer_ API so that it can be imported as a library
  into other projects.
- Make the `colorlog` Python package optional to allow _py-lambda-packer_ to be
  imported into other projects as a library more cleanly.
- Plugin support.
- Support building packages with C and C++ Python extensions.  _Thinking out
  loud...  Spin up an _EC2_ instance on the fly via something like [HashiCorp
  Packer][], build, package, destroy instance._
- Clean up _Windows_ compatibility.  (I do not have access to a _Windows_ based
  system, so any contributions here would be greatly appreciated.)
- Support packaging for other Function as a Service (FaaS) platforms provided
  by : _Azure_, _Google Cloud_, etc.


## References

### For more information

- [AWS Documentation - Creating a Deployment Package (Python)][]
- [Stackoverflow answer][] - The question pertains to AWS lambda function for
  Alexa, but the answer is generally relevant to packaging Python AWS Lambdas.


### Related projects

If you are working with the [Serverless Framework][] the following plugins
might be of interest to you:

- [serverless-wsgi][] - "Serverless plugin to deploy WSGI applications
  (Flask/Django/Pyramid etc.) and bundle Python packages".  This
  _py-lambda-packer_ is loosely based on this project.  Many thanks to the
  contributors of that project.
- [serverless-python-requirements][] - "Serverless plugin to bundle Python
  packages".

For a full list of _Serverless Framework_ plugins, refer to
[serverless/plugins][].


Other frameworks that are worth investigating are:

- [AWS Labs Chalice][] - "Python Serverless Microframework for AWS".
- [Zappa][] - "Serverless Python Web Services".

Please keep in mind that this list is not intended to be extensive.  It is only
here to help folks branch out their investigations.


[Serverless Framework]: https://serverless.com/

[serverless-wsgi]: https://github.com/logandk/serverless-wsgi
[serverless-python-requirements]: https://github.com/UnitedIncome/serverless-python-requirements
[serverless/plugins]: https://github.com/serverless/plugins

[AWS Labs Chalice]: https://github.com/awslabs/chalice
[Zappa]: https://github.com/Miserlou/Zappa

[AWS Documentation - Creating a Deployment Package (Python)]: http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
[Stackoverflow answer]: https://stackoverflow.com/a/38877273/2721824

[HashiCorp Packer]: https://www.packer.io/
