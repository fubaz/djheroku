''' Djheroku tests '''

import unittest2
from mock import MagicMock
from djheroku import sendgrid
import os

ENVIRON_DICT = {'SENDGRID_USERNAME': 'alice',
                'SENDGRID_PASSWORD': 's3cr37'}

def getitem(name):
    ''' Mock getitem '''
    return ENVIRON_DICT[name]

os.environ = MagicMock(spec_set=dict)
os.environ.__getitem__.side_effect = getitem

class TestDjheroku(unittest2.TestCase): # pylint: disable-msg=R0904
    ''' Test configuration parameters from Heroku env to Django settings '''

    def test_sendgrid_basic(self):
        ''' Test SENDGRID configuration '''
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
