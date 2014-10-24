#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from bearlib import __version__, __author__, __contact__

# use requirements.txt for dependencies
with open('requirements.txt') as f:
    required = map(lambda s: s.strip(), f.readlines())

with open('README') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='bearlib',
    version=__version__,
    description="bear's toolkit",
    long_description=readme,
    install_requires=required,
    author=__author__,
    author_email=__contact__,
    url='https://pypi.python.org/pypi/bearlib/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
