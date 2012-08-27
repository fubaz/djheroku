''' Djheroku tests '''
from __future__ import with_statement

import unittest2
from mock import MagicMock
from djheroku import sendgrid, mailgun
import os

ENVIRON_DICT = {'SENDGRID_USERNAME': 'alice',
                'SENDGRID_PASSWORD': 's3cr37',
                'MAILGUN_SMTP_LOGIN': 'bob',
                'MAILGUN_SMTP_PASSWORD': 'NoneShallPass',
                'MAILGUN_SMTP_PORT': 666,
                'MAILGUN_SMTP_SERVER': 'smtp.mailgun.com',
                'MAILGUN_API_KEY': 'key',
               }

def getitem(name):
    ''' Mock getitem '''
    return ENVIRON_DICT[name]

os.environ = MagicMock(spec_set=dict)
os.environ.__getitem__.side_effect = getitem

class TestDjheroku(unittest2.TestCase): # pylint: disable-msg=R0904
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

