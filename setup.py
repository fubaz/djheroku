#!/usr/bin/env python

from setuptools import setup

setup(name='Djheroku',
      version='0.2',
      description='Some helper functionality for binding Heroku configuration to Django',
      author='Ferrix Hovi',
      author_email='ferrix+git@ferrix.fi',
      url='http://github.com/ferrix/djheroku/',
      packages=['djheroku'],
      setup_requires=['unittest2'],
     )
