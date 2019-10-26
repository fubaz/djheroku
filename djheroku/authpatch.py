'''
Configuration strategy for python-social-auth

This will make Django prefer variables from the
environment.
'''

import os
import django
from django.core.exceptions import AppRegistryNotReady
try:
    from social.strategies.django_strategy import DjangoStrategy
except AppRegistryNotReady:
    # This is to make tests pass. This should not happen when Django
    # is properly configured
    django.setup()
    from social.strategies.django_strategy import DjangoStrategy

class DjangoEnvStrategy(DjangoStrategy): # pylint: disable=R0903,R0904
    ''' Django Strategy that reads parameters from env '''
    def get_setting(self, name):
        ''' Get individual setting '''
        setting = os.environ.get(name)
        if setting is not None:
            return setting

        setting = os.environ.get(name[len('SOCIAL_AUTH_'):])

        if setting is not None:
            return setting

        return super(DjangoEnvStrategy, self).get_setting(name)
