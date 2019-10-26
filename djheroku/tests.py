''' Djheroku tests '''
from __future__ import with_statement

# pylint: disable=R0904

import os

import unittest2
from mock import MagicMock
from django.conf import settings
import django

django.setup()  # pylint: disable=wrong-import-position

from django.http import HttpResponsePermanentRedirect, HttpRequest

from djheroku import (sendgrid, mailgun, cloudant, memcachier, identity,
                      socialregistration, allowed_hosts, autopilot,
                      social_auth, python_social_auth)
from djheroku.middleware import NoWwwMiddleware, ForceSSLMiddleware
from djheroku.middleware import PreferredDomainMiddleware
from djheroku.authpatch import DjangoEnvStrategy

ENVIRON_DICT = {'SENDGRID_USERNAME': 'alice',
                'SENDGRID_PASSWORD': 's3cr37',
                'MAILGUN_SMTP_LOGIN': 'bob',
                'MAILGUN_SMTP_PASSWORD': 'NoneShallPass',
                'MAILGUN_SMTP_PORT': 666,
                'MAILGUN_SMTP_SERVER': 'smtp.mailgun.com',
                'MAILGUN_API_KEY': 'key',
                'CLOUDANT_URL': 'http://www.google.com/',
                'MEMCACHIER_PASSWORD': 'abcdefgh',
                'MEMCACHIER_SERVERS': 'dev1.ec2.memcachier.com:11211',
                'MEMCACHIER_USERNAME': 'carol',
                'SERVER_EMAIL': 'application@example.com',
                'INSTANCE': 'djheroku-test',
                'ADMINS': 'Admin:admin@example.com,Boss:phb@example.com',
                'FACEBOOK_KEY': 'fbapp',
                'FACEBOOK_SECRET': 'fbsecret',
                'TWITTER_KEY': 'twitkey',
                'TWITTER_SECRET': 'twithush',
                'LINKEDIN_KEY': 'linkdkey',
                'LINKEDIN_SECRET': 'linkdhush',
                'ALLOWED_HOSTS': 'example.com:80, some.ly',
                'ADDONS': 'sendgrid,memcachier,socialregistration,nothing',
               }


MODIFIED_ENVIRON = {}


def getitem(name):
    ''' Mock getitem '''
    return ENVIRON_DICT[name]

def setitem(name, value):
    ''' Store mocked environment changes in an alternative dictionary '''
    print name, value
    MODIFIED_ENVIRON[name] = value

def update(values):
    ''' Redirect environment updates to an alternative dictionary '''
    MODIFIED_ENVIRON.update(values)

def envget(name, default=None):
    ''' Mock dict.get '''
    if name in ENVIRON_DICT:
        return ENVIRON_DICT[name]
    return default

def contain(key):
    ''' Mock dict.__contains__ '''
    return key in ENVIRON_DICT

def iterx():
    ''' Mock dict.__iter__ '''
    return iter(ENVIRON_DICT)

os.environ = MagicMock(spec_set=dict)
os.environ.__getitem__.side_effect = getitem
os.environ.__setitem__.side_effect = setitem
os.environ.__contains__.side_effect = contain
os.environ.__iter__.side_effect = iterx
os.environ.update.side_effect = update
os.environ.get.side_effect = envget

class TestPreferredDomainMiddleware(unittest2.TestCase):  # pylint: disable=R0903,C0301
    """ Test for middleware that redirects all requests to a preferred host """

    def setUp(self):  # pylint: disable=C0103
        self.middleware = PreferredDomainMiddleware()
        settings.PREFERRED_HOST = 'another.com'
        settings.DEBUG = False
        self.request = HttpRequest()
        self.request.path = '/test_path'
        self.request.META['SERVER_NAME'] = 'www.example.com'
        self.request.META['SERVER_PORT'] = 80
        self.request.is_secure = MagicMock(return_value=False)

    def test_disabled_by_debug(self):
        ''' No redirects happen when debug is on '''
        settings.DEBUG = True
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_redirects_to_preferred(self):
        ''' The default behavior is to redirect to the preferred host '''
        self.assertEqual('http://another.com/test_path',
                         self.middleware.process_request(
                             self.request)['Location'])

    def test_no_redirect_no_preferred_host(self):
        ''' Test with preferred host as None '''
        settings.PREFERRED_HOST = None
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_already_preferred_domain(self):
        ''' No redirect if host is already right'''
        settings.PREFERRED_HOST = 'www.example.com'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_preferred_host_empty_no_redirect(self):
        ''' Test with empty preferred host '''
        settings.PREFERRED_HOST = ''
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_host_not_defined_no_redirect(self):
        ''' No preferred host, no redirect '''
        del settings.PREFERRED_HOST
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_query_string_passed_in_redirect(self):
        ''' Query string is not lost in redirect '''
        self.request.GET = {'key': 'value'}
        self.request.META['QUERY_STRING'] = 'key=value'
        response = self.middleware.process_request(self.request)
        expected = 'http://another.com/test_path?key=value'
        self.assertEqual(expected, response['Location'])


class TestForceSSLMiddleware(unittest2.TestCase):
    ''' Tests for SSL redirection middleware '''
    def setUp(self):  # pylint: disable=C0103
        self.middleware = ForceSSLMiddleware()
        settings.FORCE_SSL = True
        settings.DEBUG = False
        self.request = HttpRequest()
        self.request.path = '/test_path'
        self.request.META['SERVER_NAME'] = 'www.example.com'
        self.request.META['SERVER_PORT'] = 80
        self.request.is_secure = MagicMock(return_value=False)

    def test_post_fails(self):
        ''' POST data is lost in redirection -> fail '''
        self.request.method = 'POST'
        with self.assertRaises(RuntimeError):
            self.middleware.process_request(self.request)

    def test_middleware_enabled_by_default(self):
        ''' The middleware is off by default '''
        del settings.FORCE_SSL
        self.assertIsInstance(self.middleware.process_request(self.request),
                              HttpResponsePermanentRedirect)

    def test_middleware_disabled_by_settings(self):
        ''' The middleware is enabled through FORCE_SSL parameter '''
        settings.FORCE_SSL = False
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_trigger_with_is_secure_false(self):
        ''' Redirect if Django HttpRequest is not secure '''
        self.assertIsInstance(self.middleware.process_request(self.request),
                              HttpResponsePermanentRedirect)

    def test_do_not_trigger_with_is_secure(self):
        ''' Do not redirect when request is secure '''
        self.request.is_secure.return_value = True
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_do_not_trigger_with_debug(self):
        ''' Do not redirect when DEBUG is on '''
        settings.DEBUG = True
        self.request.META["HTTP_X_FORWARDED_PROTO"] = 'http'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_trigger_with_header(self):
        ''' Redirect when forwarded protocol is http '''
        self.request.META["HTTP_X_FORWARDED_PROTO"] = 'http'
        self.assertIsInstance(self.middleware.process_request(self.request),
                              HttpResponsePermanentRedirect)

    def test_do_not_trigger_with_https_header(self):
        ''' Do not redirect when protocol is already https '''
        self.request.META["HTTP_X_FORWARDED_PROTO"] = 'https'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_sts_header_on(self):
        ''' STS headers get added to response '''
        response = self.middleware.process_response(self.request, {})
        self.assertIn('Strict-Transport-Security', response)

    def tests_sts_header_off(self):
        ''' STS headers disabled by settings '''
        settings.SSL_USE_STS_HEADER = False
        response = self.middleware.process_response(self.request, {})
        self.assertNotIn('Strict-Transport-Security', response)

class TestNoWwwMiddleware(unittest2.TestCase):  # pylint: disable=R0904
    ''' Tests for the WWW removal middleware '''

    def setUp(self):  # pylint: disable=C0103
        ''' All tests will need an instance of the middleware '''
        self.middleware = NoWwwMiddleware()
        settings.NO_WWW = True
        self.request = HttpRequest()
        self.request.path = '/test_path'
        self.request.META['SERVER_NAME'] = 'www.example.com'
        self.request.META['SERVER_PORT'] = 80

    def test_middleware_disabled(self):
        ''' Test that middleware does nothing when it is off '''
        settings.NO_WWW = False
        self.assertEqual(None, self.middleware.process_request(self.request))

    def test_middleware_enabled(self):
        ''' Test that www gets removed from URL properly '''
        response = self.middleware.process_request(self.request)
        self.assertIsInstance(response, HttpResponsePermanentRedirect)
        self.assertEqual(301, response.status_code)
        self.assertFalse('www.example.com' in response['Location'])

    def test_no_www_in_input(self):
        ''' Test that URLs with no www do not get redirected '''
        self.request.META['SERVER_NAME'] = 'host.example.com'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_www_not_in_beginning(self):
        ''' www somewhere in the middle of the URL should not be removed '''
        self.request.META['SERVER_NAME'] = 'host.www.example.com'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_www_in_domain(self):
        ''' Having www in the domain part should not redirect '''
        self.request.META['SERVER_NAME'] = 'wwwexample.com'
        self.assertIsNone(self.middleware.process_request(self.request))
        self.request.META['SERVER_NAME'] = 'wwwa.example.com'
        self.assertIsNone(self.middleware.process_request(self.request))

    def test_ssl(self):
        ''' Test that secure requests are redirected to non-www URLs '''
        self.request.is_secure = MagicMock(return_value=True)
        response = self.middleware.process_request(self.request)
        self.assertTrue(response['Location'].startswith('https://example.com'))

    def test_query_string(self):
        ''' If there are query parameters, they remain after redirect '''
        self.request.GET = {'key': 'value'}
        self.request.META['QUERY_STRING'] = 'key=value'
        response = self.middleware.process_request(self.request)
        self.assertTrue(response['Location'].startswith('http://example.com/'))
        self.assertIn('?key=value', response['Location'])

class TestDjheroku(unittest2.TestCase):  # pylint: disable=R0904
    ''' Test configuration parameters from Heroku env to Django settings '''

    def test_sendgrid_basic(self):
        ''' Test Sendgrid configuration '''
        result = sendgrid()
        self.assertEqual('alice', result['EMAIL_HOST_USER'])
        self.assertEqual('s3cr37', result['EMAIL_HOST_PASSWORD'])
        self.assertTrue(result['EMAIL_USE_TLS'])
        self.assertTrue('sendgrid' in result['EMAIL_HOST'])
        self.assertEqual(587, result['EMAIL_PORT'])

    def test_sendgrid_missing_env(self):
        ''' Test that variables are not set if environment is not present '''
        del ENVIRON_DICT['SENDGRID_USERNAME']

        result = sendgrid()
        self.assertIsInstance(result, dict)
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_USER']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_PASSWORD']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST']
        with self.assertRaises(KeyError):
            print result['EMAIL_PORT']
        with self.assertRaises(KeyError):
            print result['EMAIL_USE_TLS']

        ENVIRON_DICT['SENDGRID_USERNAME'] = 'carol'
        del ENVIRON_DICT['SENDGRID_PASSWORD']

        result = sendgrid()
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_USER']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_PASSWORD']

    def test_mailgun_basic(self):
        ''' Test Mailgun configuration '''
        result = mailgun()
        self.assertEqual('bob', result['EMAIL_HOST_USER'])
        self.assertEqual('NoneShallPass', result['EMAIL_HOST_PASSWORD'])
        self.assertTrue('mailgun' in result['EMAIL_HOST'])
        self.assertEqual(666, result['EMAIL_PORT'])
        self.assertFalse(result['EMAIL_USE_TLS'])
        ENVIRON_DICT['MAILGUN_SMTP_PORT'] = 587
        result = mailgun()
        self.assertTrue(result['EMAIL_USE_TLS'])

    def test_mailgun_missing_env(self):
        ''' Test that variables are not set if environment is not present '''
        del ENVIRON_DICT['MAILGUN_API_KEY']
        result = mailgun()
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_USER']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_PASSWORD']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST']
        with self.assertRaises(KeyError):
            print result['EMAIL_PORT']
        with self.assertRaises(KeyError):
            print result['EMAIL_USE_TLS']
        with self.assertRaises(KeyError):
            print result['MAILGUN_API_KEY']

    def test_cloudant(self):
        ''' Test Cloudant variables '''
        result = cloudant()
        self.assertEqual('http://www.google.com/', result['CLOUDANT_URL'])
        del ENVIRON_DICT['CLOUDANT_URL']
        result = cloudant()
        with self.assertRaises(KeyError):
            print result['CLOUDANT_URL']

    def test_memcachier(self):
        ''' Test Memcachier variables '''
        result = memcachier()
        self.assertEqual('abcdefgh', result['MEMCACHE_PASSWORD'])
        self.assertEqual('carol', result['MEMCACHE_USERNAME'])
        self.assertEqual('dev1.ec2.memcachier.com:11211',
                         result['MEMCACHE_SERVERS'])
        self.assertEqual('dev1.ec2.memcachier.com:11211',
                         result['CACHES']['default']['LOCATION'])
        self.assertEqual(ENVIRON_DICT['MEMCACHIER_SERVERS'],
                         MODIFIED_ENVIRON['MEMCACHE_SERVERS'])
        self.assertEqual('django_pylibmc.memcached.PyLibMCCache',
                         result['CACHES']['default']['BACKEND'])
        del ENVIRON_DICT['MEMCACHIER_SERVERS']
        result = memcachier()
        self.assertEqual('django.core.cache.backends.locmem.LocMemCache',
                         result['CACHES']['default']['BACKEND'])

    def test_identity(self):
        ''' Test Django email settings '''
        result = identity()
        self.assertEqual('application@example.com', result['SERVER_EMAIL'])
        self.assertEqual('[djheroku-test] ', result['EMAIL_SUBJECT_PREFIX'])
        self.assertIn('ADMINS', result)
        self.assertIn(['Admin', 'admin@example.com'], result['ADMINS'])
        self.assertEqual(2, len(result['ADMINS']))
        self.assertEqual(['Boss', 'phb@example.com'], result['ADMINS'][1])

        del ENVIRON_DICT['ADMINS']
        del ENVIRON_DICT['SERVER_EMAIL']
        del ENVIRON_DICT['INSTANCE']
        result = identity()
        self.assertNotIn('ADMINS', result)
        self.assertNotIn('SERVER_EMAIL', result)
        self.assertNotIn('EMAIL_SUBJECT_PREFIX', result)

    def test_socialregistration(self):
        ''' Test API key settings '''
        result = socialregistration()
        self.assertEqual('fbapp', result['FACEBOOK_APP_ID'])
        self.assertEqual('fbsecret', result['FACEBOOK_SECRET_KEY'])
        self.assertEqual('twitkey', result['TWITTER_CONSUMER_KEY'])
        self.assertEqual('twithush', result['TWITTER_CONSUMER_SECRET_KEY'])
        self.assertEqual('linkdkey', result['LINKEDIN_CONSUMER_KEY'])
        self.assertEqual('linkdhush', result['LINKEDIN_CONSUMER_SECRET_KEY'])

        del ENVIRON_DICT['FACEBOOK_SECRET']
        del ENVIRON_DICT['TWITTER_KEY']
        result = socialregistration()
        self.assertNotIn('FACEBOOK_APP_ID', result)
        self.assertNotIn('TWITTER_CONSUMER_SECRET_KEY', result)
        self.assertIn('LINKEDIN_CONSUMER_KEY', result)

    def test_social_auth(self):
        ''' Test Sentry settings '''
        result = social_auth()
        self.assertEqual('fbapp', result['FACEBOOK_APP_ID'])
        self.assertEqual('fbsecret', result['FACEBOOK_API_SECRET'])

    def test_python_social_auth(self):
        ''' Test python-social-auth configuration '''
        result = python_social_auth()
        self.assertIn('SOCIAL_AUTH_STRATEGY', result)

    def test_no_social_package(self):
        ''' No fail when python-social-auth is not installed '''
        def raise_import_error(*args, **kwargs): # pylint: disable=W0613
            ''' Force an ImportError with this mock '''
            raise ImportError('This is what happens!')

        import imp
        original = imp.find_module
        imp.find_module = raise_import_error

        result = python_social_auth()

        try:
            self.assertNotIn('SOCIAL_AUTH_STRATEGY', result)
        finally:
            imp.find_module = original

    def test_allowed_hosts(self):
        ''' Test host whitelist '''
        result = allowed_hosts()
        self.assertIn('ALLOWED_HOSTS', result)
        self.assertIn('example.com:80', result['ALLOWED_HOSTS'])
        self.assertIn('some.ly', result['ALLOWED_HOSTS'])

        del ENVIRON_DICT['ALLOWED_HOSTS']
        result = allowed_hosts()
        self.assertNotIn('ALLOWED_HOSTS', result)

    def test_autopilot(self):
        ''' Test fully automatic configuration '''
        conf = {}
        autopilot(conf)

        self.assertIn('MEMCACHE_SERVERS', conf)
        self.assertIn('EMAIL_HOST_USER', conf)
        self.assertIn('SERVER_EMAIL', conf)
        self.assertNotIn('CLOUDANT_URL', conf)

        del ENVIRON_DICT['ADDONS']
        conf = {}
        self.assertNotIn('MEMCACHE_SERVERS', conf)

class TestDjangoEnvStrategy(unittest2.TestCase): # pylint: disable=R0903
    '''
    Tests for python-social-auth Django patch
    '''
    def test_get_setting(self):
        ''' Test the only thing in new Django strategy '''
        ENVIRON_DICT['SOCIAL_AUTH_TWITTER_SECRET'] = 'overridden'
        strategy = DjangoEnvStrategy(None)
        self.assertEqual('twitkey',
                         strategy.get_setting('SOCIAL_AUTH_TWITTER_KEY'))
        self.assertEqual('overridden',
                         strategy.get_setting('SOCIAL_AUTH_TWITTER_SECRET'))
        with self.assertRaises(AttributeError):
            strategy.get_setting('SOCIAL_AUTH_NOT_SET')
