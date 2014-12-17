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


def env_to_env(mappings):
    ''' Copy environment variables others variables '''
    result = {}
    for new_env, env in mappings.items():
        try:
            result[new_env] = os.environ[env]
        except:
            print 'Problem fetching environment variable %s' % env
            raise

    os.environ.update(result)

    return result


def sendgrid():
    ''' Map Sendgrid environment variables to Django '''
    mapping = {}
    mapping['EMAIL_HOST_USER'] = 'SENDGRID_USERNAME'
    mapping['EMAIL_HOST_PASSWORD'] = 'SENDGRID_PASSWORD'
    try:
        result = env_to_django(mapping)
    except:  # pylint: disable=W0702
        return {}
    result['EMAIL_HOST'] = 'smtp.sendgrid.net'
    result['EMAIL_PORT'] = 587
    result['EMAIL_USE_TLS'] = True

    return result


def memcachier():
    ''' Map Memcachier environment variables to Django '''
    mapping = {}
    mapping['MEMCACHE_SERVERS'] = 'MEMCACHIER_SERVERS'
    mapping['MEMCACHE_USERNAME'] = 'MEMCACHIER_USERNAME'
    mapping['MEMCACHE_PASSWORD'] = 'MEMCACHIER_PASSWORD'
    try:
        result = env_to_env(mapping)
        caches = {
            'default': {
                'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
                'LOCATION': result['MEMCACHE_SERVERS'],
                'TIMEOUT': 500,
                'BINARY': True
            }
        }
        result['CACHES'] = caches
        return result
    except:  # pylint: disable=W0702
        caches = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        }
        return {'CACHES': caches}


def mailgun():
    ''' Map Mailgun environment variables to Django '''
    mapping = {}
    mapping['EMAIL_HOST'] = 'MAILGUN_SMTP_SERVER'
    mapping['EMAIL_PORT'] = 'MAILGUN_SMTP_PORT'
    mapping['EMAIL_HOST_USER'] = 'MAILGUN_SMTP_LOGIN'
    mapping['EMAIL_HOST_PASSWORD'] = 'MAILGUN_SMTP_PASSWORD'
    mapping['MAILGUN_API_KEY'] = 'MAILGUN_API_KEY'
    try:
        result = env_to_django(mapping)
    except:  # pylint: disable=W0702
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
    except:  # pylint: disable=W0702
        return {}

    return result


def identity():
    ''' Maps outgoing email settings and application name to environment '''
    result = {}

    server_email = os.environ.get('SERVER_EMAIL')
    if server_email:
        result['SERVER_EMAIL'] = server_email

    instance = os.environ.get('INSTANCE')
    if instance:
        result['EMAIL_SUBJECT_PREFIX'] = '[{0}] '.format(instance)

    if 'ADMINS' in os.environ:
        result['ADMINS'] = [
            x.split(':') for x in os.environ['ADMINS'].split(',')]

    return result


def allowed_hosts():
    ''' Map allowed hosts from environment to Django '''
    mapping = {}
    try:
        mapping['ALLOWED_HOSTS'] = [
            x.strip() for x in os.environ['ALLOWED_HOSTS'].split(',')]
    except KeyError:
        pass

    return mapping
