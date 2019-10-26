'''
Let's get this straight.

There are n+1 (n->infinity) names for the OAuthy credential pairs:
api key, api secret, consumer key, app id, api secret, app key...

Different apps name them however they please and we should store
them exactly once.

See the next functions for proof.

The only real exception to this is `python-social-auth`
'''
import os
import imp


def social_slurp(mapping):
    '''
    Generic function to map social authentication parameters
    '''
    def inner_slurp(service, app_id, api_key):
        ''' inner loop '''
        service_keys = {}
        service_name = service.upper()
        try:
            service_keys[app_id] = os.environ[service_name+'_KEY']
            service_keys[api_key] = os.environ[service_name+'_SECRET']
        except KeyError:
            return {}

        return service_keys

    result = {}

    for app, (app_id, api_key) in mapping.iteritems():
        result.update(inner_slurp(app, app_id, api_key))

    return result


def social_auth():
    '''
    Maps API keys to django-social-auth settings (Sentry subset)

    On the left, the friendly name of the service
    On the right, the Django conf variables expected for the particular
    library.
    '''
    service_mapping = {
        'facebook': ('FACEBOOK_APP_ID', 'FACEBOOK_API_SECRET'),
        'twitter': ('TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_KEY'),
        'trello': ('TRELLO_API_KEY', 'TRELLO_API_SECRET'),
        'google': ('GOOGLE_OAUTH2_CLIENT_ID', 'GOOGLE_OAUTH2_CLIENT_SECRET'),
        'github': ('GITHUB_APP_ID', 'GITHUB_API_SECRET'),
        }

    return social_slurp(service_mapping)


def socialregistration():
    '''
    Maps API keys to django-socialregistration settings

    On the left, the friendly name of the service
    On the right, the Django conf variables expected for the particular
    library.
    '''
    service_mapping = {
        'facebook': ('FACEBOOK_APP_ID', 'FACEBOOK_SECRET_KEY'),
        'foursquare': ('FOURSQUARE_CLIENT_ID', 'FOURSQUARE_CLIENT_SECRET'),
        'github': ('GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET'),
        'google': ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'),
        'instagram': ('INSTAGRAM_CLIENT_ID', 'INSTAGRAM_CLIENT_SECRET'),
        'linkedin': ('LINKEDIN_CONSUMER_KEY', 'LINKEDIN_CONSUMER_SECRET_KEY'),
        'tumblr': ('TUMBLR_CONSUMER_KEY', 'TUMBLR_CONSUMER_SECRET_KEY'),
        'twitter': ('TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET_KEY'),
        }

    return social_slurp(service_mapping)


def python_social_auth():
    '''
    Capture python-social-auth strategy and prefer environment
    '''
    try:
        imp.find_module('social')

        return {'SOCIAL_AUTH_STRATEGY': 'djheroku.authpatch.DjangoEnvStrategy'}
    except ImportError:
        return {}
