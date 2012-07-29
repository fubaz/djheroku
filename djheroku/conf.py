import os

def env_to_django(mappings):
    result = {}
    for django_var, env in mappings.items():
        try:
            result[django_var] = os.environ[env]
        except:
            print 'Problem fetching environment variable %s' % env
            raise

    return result

def sendgrid():
    mapping = {}
    mapping['EMAIL_HOST_USER']     = 'SENDGRID_USERNAME'
    mapping['EMAIL_HOST_PASSWORD'] = 'SENDGRID_PASSWORD'
    try:
        result = env_to_django(mapping)
    except:
        return {}
    result['EMAIL_HOST']    = 'smtp.sendgrid.net'
    result['EMAIL_PORT']    = 587
    result['EMAIL_USE_TLS'] = True

    return result

def mailgun():
    mapping = {}
    mapping['EMAIL_HOST']          = 'MAILGUN_SMTP_SERVER'
    mapping['EMAIL_PORT']          = 'MAILGUN_SMTP_PORT'
    mapping['EMAIL_HOST_USER']     = 'MAILGUN_SMTP_LOGIN'
    mapping['EMAIL_HOST_PASSWORD'] = 'MAILGUN_SMTP_PASSWORD'
    mapping['MAILGUN_API_KEY']     = 'MAILGUN_API_KEY'
    try:
        result = env_to_django(mapping)
    except:
        return {}
    result['EMAIL_PORT'] = int(result['EMAIL_PORT'])
    result['EMAIL_USE_TLS'] = result['EMAIL_PORT'] == 587

    return result

def cloudant():
    mapping = {}
    mapping['CLOUDANT_URL'] = 'CLOUDANT_URL'
    try:
        result = env_to_django(mapping)
    except:
        return {}

    return result

