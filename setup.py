#!/usr/bin/env python
''' Setuptools installation script for Djheroku '''
from __future__ import with_statement
import os

from setuptools import setup

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'djheroku/_version.py'
versioneer.versionfile_build = None
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'Djheroku-' # dirname like 'myproject-1.2.0'

os.environ['DJANGO_SETTINGS_MODULE'] = 'djheroku.fixture'

requirements = ''
with open('requirements.txt') as req:
    requirements = req.read()

test_requirements = ''
if os.path.exists('requirements-test.txt'):
    with open('requirements-test.txt') as reqtest:
        test_requirements = reqtest.read()

setup(name='Djheroku',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Some helper functionality for binding Heroku configuration to Django',
      author='Ferrix Hovi',
      author_email='ferrix+git@ferrix.fi',
      url='http://github.com/fubaz/djheroku/',
      packages=['djheroku'],
      install_requires=requirements,
      setup_requires=['nose>=1.2.1'],
      tests_require=test_requirements,
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Framework :: Django",
      ]
)
