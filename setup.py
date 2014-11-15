#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

from bearlib import __version__, __author__, __contact__

with open('README.rst') as f:
    readme = f.read()

setup(name='bearlib',
      version=__version__,
      author=__author__,
      author_email=__contact__,
      url='http://github.com/bear/bearlib',
      download_url='https://pypi.python.org/pypi/bearlib/',
      description="bear's toolkit",
      license='MIT',
      packages=find_packages(exclude=('tests', 'docs')),
      long_description=readme,
      platforms=['Any'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)
