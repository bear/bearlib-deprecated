#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import sys
import re
import codecs

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

cwd = os.path.abspath(os.path.dirname(__file__))

class PyTest(TestCommand):
    """You can pass a single string of arguments using the
    --pytest-args or -a command-line option:
        python setup.py test -a "--durations=5"
    is equivalent to running:
        py.test --durations=5
    """
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--strict', '--verbose', '--tb=long', 'tests']

    def finalize_options(self):
        TestCommand.finalize_options(self)

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read(filename):
    with codecs.open(os.path.join(cwd, filename), 'rb', 'utf-8') as h:
        return h.read()

metadata = read(os.path.join(cwd, 'bearlib', '__init__.py'))

def extract_metaitem(meta):
    # swiped from https://hynek.me 's attr package
    meta_match = re.search(r"""^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]""".format(meta=meta),
                           metadata, re.MULTILINE)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))

if __name__ == '__main__':
  setup(name='bearlib',
        version=extract_metaitem('version'),
        license=extract_metaitem('license'),
        description=extract_metaitem('description'),
        long_description=read('README.rst'),
        author=extract_metaitem('author'),
        author_email=extract_metaitem('email'),
        maintainer=extract_metaitem('author'),
        maintainer_email=extract_metaitem('email'),
        url=extract_metaitem('url'),
        download_url=extract_metaitem('download_url'),
        packages=find_packages(exclude=('tests', 'docs')),
        platforms=['Any'],
        setup_requires=['pytest-runner'],
        tests_require=['pytest'],
        classifiers=[ 'Development Status :: 5 - Production/Stable',
                      'Intended Audience :: Developers',
                      'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
                      'Topic :: Software Development :: Libraries :: Python Modules',
                      'Operating System :: Unix',
                      'Operating System :: POSIX',
                      'Operating System :: Microsoft :: Windows',
                      'Programming Language :: Python',
                      'Programming Language :: Python :: 2.7',
                      'Programming Language :: Python :: 3',
                      'Programming Language :: Python :: 3.5',
                      # 'Programming Language :: Python :: Implementation :: CPython',
                      # 'Programming Language :: Python :: Implementation :: PyPy',
                      # 'Programming Language :: Python :: Implementation :: IronPython',
                      # 'Programming Language :: Python :: Implementation :: Jython',
                      # 'Programming Language :: Python :: Implementation :: Stackless',
        ]
  )
