Djheroku
========

Djheroku is a helper script that reads Heroku configuration from environment
variables and injects them to Django configuration.

[![Build Status](https://secure.travis-ci.org/fubaz/djheroku.png?branch=master)](http://travis-ci.org/fubaz/djheroku)

Configuration helpers
---------------------

Example:

    # settings.py
    from djheroku import sendgrid
    vars().update(sendgrid())

This is equivalent of typing in:

    # settings.py
    import os
    
    if 'SENDGRID_USERNAME' in os.environ and 'SENDGRID_PASSWORD' in os.environ:
        EMAIL_HOST = 'smtp.sendgrid.net'
        EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
        EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True

If any of the variables are not present, the configuration will be left as it
is. Currently there are two helpers: `sendgrid()` and `mailgun()`.

Middleware
----------

There are three middleware classes in Djheroku. They are used to redirect
permanently from one URL to another.

* `NoWwwMiddleware` removed www. from URLs of incoming requests.
  The opposite is built-in functionality of Django. Enable this Middleware
  and set NO_WWW = True in settings.py to activate.
* `PreferredDomainMiddleware` redirects all domains directed to the
  application to a preferred one.
* `ForceSSLMiddleware` redirects all non-SSL connections to a secure
  connection.

Each of these middlewares does one thing only and combined they will lead
into three separate redirects or even a eternal loop if configured
properly wrong.
