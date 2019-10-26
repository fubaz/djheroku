''' Djheroku for populating Heroku environment variables to Django '''
import os

from djheroku.conf import (sendgrid, mailgun, cloudant, memcachier, identity,
                           allowed_hosts)
from djheroku.auth import social_auth, socialregistration, python_social_auth

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

def autopilot(conf):
    ''' Read list of addons to configure in environment '''
    addons = [x.strip() for x in os.environ.get('ADDONS', '').split(',')]

    addon_map = {'sendgrid': sendgrid,
                 'mailgun': mailgun,
                 'memcachier': memcachier,
                 'cloudant': cloudant,
                 'social': socialregistration,
                 'socialregistration': socialregistration,
                 'social_auth': social_auth,
                 'python_social_auth': python_social_auth,
                }

    conf.update(identity())
    conf.update(allowed_hosts())

    for addon in addons:
        if addon in addon_map:
            conf.update(addon_map[addon]())

    return conf
