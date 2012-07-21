Djheroku
========

Djheroku is a helper script that reads Heroku configuration from environment
variables and injects them to Django configuration.

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
