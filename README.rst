Djheroku
========

Djheroku is a helper script that reads Heroku configuration from environment
variables and injects them to Django configuration.


.. image:: https://secure.travis-ci.org/fubaz/djheroku.png?branch=master
    :target: http://travis-ci.org/fubaz/djheroku
    :alt: Build Status

.. image:: https://coveralls.io/repos/ferrix/djheroku/badge.png
    :target: https://coveralls.io/r/ferrix/djheroku
    :alt: Test Coverage

.. image:: https://requires.io/github/fubaz/djheroku/requirements.svg?branch=master
     :target: https://requires.io/github/fubaz/djheroku/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://img.shields.io/pypi/v/djheroku.svg
    :target: https://pypi.python.org/pypi/djheroku/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/djheroku.svg
    :target: https://pypi.python.org/pypi/djheroku/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/l/djheroku.svg
    :target: https://pypi.python.org/pypi/djheroku/
    :alt: License

Autopilot for Heroku settings
-----------------------------

This is an easier way to control what Django does. Just add
a few lines to your settings.py::

    from djheroku import autopilot
    autopilot(vars())

Then you can make runtime changes to your application settings::

    heroku addons:add sendgrid
    heroku config:set ADDONS=sendgrid
    heroku addons:add memcachier
    heroku config:set ADDONS=sendgrid,memcachier

Djheroku will change the variables accordingly.

Configuration helpers
---------------------

Example::

    # settings.py
    from djheroku import sendgrid
    vars().update(sendgrid())

This is equivalent of typing in::

    # settings.py
    import os
    
    if 'SENDGRID_USERNAME' in os.environ and 'SENDGRID_PASSWORD' in os.environ:
        EMAIL_HOST = 'smtp.sendgrid.net'
        EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
        EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True

If any of the variables are not present, the configuration will be left as it
is. Currently there are two helpers: ``sendgrid()`` and ``mailgun()``.

Middleware
----------

There are three middleware classes in Djheroku. They are used to redirect
permanently from one URL to another.

* ``NoWwwMiddleware`` removed www. from URLs of incoming requests.
  The opposite is built-in functionality of Django. Enable this Middleware
  and set NO_WWW = True in settings.py to activate.
* ``PreferredDomainMiddleware`` redirects all domains directed to the
  application to a preferred one.
* ``ForceSSLMiddleware`` redirects all non-SSL connections to a secure
  connection.

Each of these middlewares does one thing only and combined they will lead
into three separate redirects or even a eternal loop if configured
properly wrong.
