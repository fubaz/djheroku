''' Map environment variables from Heroku to Django configuration '''

import os

def env_to_django(mappings):
    ''' Copy environment variables to Django configuration variables '''
    result = {}
    for django_var, env in mappings.items():
        try:
            result[django_var] = os.environ[env]
        except:
            print 'Problem fetching environment variable %s' % env
            raise

    return result

def sendgrid():
    ''' Map Sendgrid environment variables to Django '''
    mapping = {}
    mapping['EMAIL_HOST_USER']     = 'SENDGRID_USERNAME'
    mapping['EMAIL_HOST_PASSWORD'] = 'SENDGRID_PASSWORD'
    try:
        result = env_to_django(mapping)
    except: # pylint: disable-msg=W0702
        return {}
    result['EMAIL_HOST']    = 'smtp.sendgrid.net'
    result['EMAIL_PORT']    = 587
    result['EMAIL_USE_TLS'] = True

    return result

def mailgun():
    ''' Map Mailgun environment variables to Django '''
    mapping = {}
    mapping['EMAIL_HOST']          = 'MAILGUN_SMTP_SERVER'
    mapping['EMAIL_PORT']          = 'MAILGUN_SMTP_PORT'
    mapping['EMAIL_HOST_USER']     = 'MAILGUN_SMTP_LOGIN'
    mapping['EMAIL_HOST_PASSWORD'] = 'MAILGUN_SMTP_PASSWORD'
    mapping['MAILGUN_API_KEY']     = 'MAILGUN_API_KEY'
    try:
        result = env_to_django(mapping)
    except: # pylint: disable-msg=W0702
        return {}
    result['EMAIL_PORT'] = int(result['EMAIL_PORT'])
    result['EMAIL_USE_TLS'] = result['EMAIL_PORT'] == 587

    return result

def cloudant():
    ''' Map Cloudant URL to CLOUDANT_URL on Django '''
    mapping = {}
    mapping['CLOUDANT_URL'] = 'CLOUDANT_URL'
    try:
        result = env_to_django(mapping)
    except: # pylint: disable-msg=W0702
        return {}

    return result

