''' Djheroku tests '''
from __future__ import with_statement

import unittest2
from mock import MagicMock
from djheroku import sendgrid, mailgun, cloudant
import os

from django.conf import settings

settings.configure(DEBUG=True, DATABASES={'default': dict()})

from django.http import HttpResponsePermanentRedirect, HttpRequest
from djheroku.middleware import NoWwwMiddleware, ForceSSLMiddleware

ENVIRON_DICT = {'SENDGRID_USERNAME': 'alice',
                'SENDGRID_PASSWORD': 's3cr37',
                'MAILGUN_SMTP_LOGIN': 'bob',
                'MAILGUN_SMTP_PASSWORD': 'NoneShallPass',
                'MAILGUN_SMTP_PORT': 666,
                'MAILGUN_SMTP_SERVER': 'smtp.mailgun.com',
                'MAILGUN_API_KEY': 'key',
                'CLOUDANT_URL': 'http://www.google.com/',
                }


def getitem(name):
    ''' Mock getitem '''
    return ENVIRON_DICT[name]

os.environ = MagicMock(spec_set=dict)
os.environ.__getitem__.side_effect = getitem


class TestForceSSLMiddleware(unittest2.TestCase):
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
        del(settings.FORCE_SSL)
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


class TestNoWwwMiddleware(unittest2.TestCase):  # pylint: disable-msg=R0904
    ''' Tests for the WWW removal middleware '''

    def setUp(self):  # pylint: disable-msg=C0103
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
        self.assertEquals(None, self.middleware.process_request(self.request))

    def test_middleware_enabled(self):
        ''' Test that www gets removed from URL properly '''
        response = self.middleware.process_request(self.request)
        self.assertIsInstance(response, HttpResponsePermanentRedirect)
        self.assertEquals(301, response.status_code)
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


class TestDjheroku(unittest2.TestCase):  # pylint: disable-msg=R0904
    ''' Test configuration parameters from Heroku env to Django settings '''

    def test_sendgrid_basic(self):
        ''' Test Sendgrid configuration '''
        result = sendgrid()
        self.assertEquals('alice', result['EMAIL_HOST_USER'])
        self.assertEquals('s3cr37', result['EMAIL_HOST_PASSWORD'])
        self.assertTrue(result['EMAIL_USE_TLS'])
        self.assertTrue('sendgrid' in result['EMAIL_HOST'])
        self.assertEquals(587, result['EMAIL_PORT'])

    def test_sendgrid_missing_env(self):
        ''' Test that variables are not set if environment is not present '''
        del(ENVIRON_DICT['SENDGRID_USERNAME'])

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
        del(ENVIRON_DICT['SENDGRID_PASSWORD'])

        result = sendgrid()
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_USER']
        with self.assertRaises(KeyError):
            print result['EMAIL_HOST_PASSWORD']

    def test_mailgun_basic(self):
        ''' Test Mailgun configuration '''
        result = mailgun()
        self.assertEquals('bob', result['EMAIL_HOST_USER'])
        self.assertEquals('NoneShallPass', result['EMAIL_HOST_PASSWORD'])
        self.assertTrue('mailgun' in result['EMAIL_HOST'])
        self.assertEquals(666, result['EMAIL_PORT'])
        self.assertFalse(result['EMAIL_USE_TLS'])
        ENVIRON_DICT['MAILGUN_SMTP_PORT'] = 587
        result = mailgun()
        self.assertTrue(result['EMAIL_USE_TLS'])

    def test_mailgun_missing_env(self):
        ''' Test that variables are not set if environment is not present '''
        del(ENVIRON_DICT['MAILGUN_API_KEY'])
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
        self.assertEquals('http://www.google.com/', result['CLOUDANT_URL'])
        del(ENVIRON_DICT['CLOUDANT_URL'])
        result = cloudant()
        with self.assertRaises(KeyError):
            print result['CLOUDANT_URL']
