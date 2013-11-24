#noinspection PyUnresolvedReferences
from settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fcs',
        'USER': 'fcs',
        'PASSWORD': 'fcs',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

