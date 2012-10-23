#!/usr/bin/env python
''' Setuptools installation script for Djheroku '''
from __future__ import with_statement
import os

from setuptools import setup

requirements = ''
with open('requirements.txt') as req:
    requirements = req.read()

setup_requirements = ''
with open('requirements-test.txt') as reqset:
    setup_requirements = reqset.read()

version = '0.3'

minor_version = os.environ.get('DJHEROKU_MINOR_VERSION', None)

if minor_version:
    version = version + '.' + minor_version

setup(name='Djheroku',
      version=version,
      description='Some helper functionality for binding Heroku configuration to Django',
      author='Ferrix Hovi',
      author_email='ferrix+git@ferrix.fi',
      url='http://github.com/ferrix/djheroku/',
      packages=['djheroku'],
      install_requires=requirements,
      setup_requires=setup_requirements,
      )
