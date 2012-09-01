#!/usr/bin/env python
''' Setuptools installation script for Djheroku '''

from setuptools import setup

requirements = ''
with open('requirements.txt') as req:
    requirements = req.read()

setup(name='Djheroku',
      version='0.2',
      description='Some helper functionality for binding Heroku configuration to Django',
      author='Ferrix Hovi',
      author_email='ferrix+git@ferrix.fi',
      url='http://github.com/ferrix/djheroku/',
      packages=['djheroku'],
      install_requires=requirements,
      )
