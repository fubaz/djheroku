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

if os.path.exists('.git'):
    import commands
    _, __version__ = commands.getstatusoutput('git describe --tags')
    with file('version.txt', 'wb') as verfile:
        verfile.write(__version__)
elif os.path.exists('version.txt'):
    with file('version.txt', 'rb') as verfile:
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
      setup_requires=setup_requirements,
)
