#!/usr/bin/env python
''' Setuptools installation script for Djheroku '''
from __future__ import with_statement
import os

from setuptools import setup

os.environ['DJANGO_SETTINGS_MODULE'] = 'djheroku.fixture'

requirements = ''
with open('requirements.txt') as req:
    requirements = req.read()

test_requirements = ''
if os.path.exists('requirements-test.txt'):
    with open('requirements-test.txt') as reqtest:
        test_requirements = reqtest.read()

version_file = 'pkg_version.txt'

if os.path.exists('.git'):
    import commands
    _, __version__ = commands.getstatusoutput('git describe --tags')
    with file(version_file, 'wb') as verfile:
        verfile.write(__version__)
elif os.path.exists(version_file):
    with file(version_file, 'rb') as verfile:
        __version__ = verfile.readlines()[0].strip()
else:
    __version__ = 'unknown'

setup(name='Djheroku',
      version=__version__,
      description='Some helper functionality for binding Heroku configuration to Django',
      author='Ferrix Hovi',
      author_email='ferrix+git@ferrix.fi',
      url='http://github.com/ferrix/djheroku/',
      packages=['djheroku'],
      install_requires=requirements,
      setup_requires=['nose>=1.2.1'],
      tests_require=test_requirements,
)
