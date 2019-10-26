''' Test fixture for minimal Django conf '''
SECRET_KEY = 'a'
DEBUG = True
DATABASES = {'default': {}}
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ['django.contrib.contenttypes']
