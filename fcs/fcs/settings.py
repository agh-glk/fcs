"""
Django settings for fcs project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&7(_46g)wlj@hk6^1cvar)blnrzaz#jdx51iee+0htkq7t1r@5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'fcs.manager',
    'django_pytest',
    'django.contrib.sites',
    'accounts',
    'userena',
    'guardian',
    'rest_framework',
    'rest_framework_swagger',
    'fcs.backend',
    'widget_tweaks',
    'oauth2_provider',
    'django_tables2',
    'huey.djhuey',
)

AUTH_USER_MODEL = 'manager.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fcs.manager.middleware.AutoLogout',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages'
)

#Time in minutes until inactive user is logged out
AUTO_LOGOUT_DELAY = 15

ROOT_URLCONF = 'fcs.urls'

WSGI_APPLICATION = 'fcs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


TEST_RUNNER = 'django_pytest.test_runner.TestRunner'

# Database used for tests?
DATABASE_NAME = 'test_db'

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'}
}

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

#Userena
AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ANONYMOUS_USER_ID = -1

AUTH_PROFILE_MODULE = "accounts.UserProfile"

LOGIN_REDIRECT_URL = '/'

USERENA_ACTIVATION_REQUIRED = True
USERENA_DISABLE_PROFILE_LIST = True

USERENA_SIGNIN_REDIRECT_URL = '/'

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

#Huey - periodic tasks
HUEY = {
    'backend': 'huey.backends.redis_backend',  
    'name': 'unique name',
    'connection': {'host': 'localhost', 'port': 6379},
    'always_eager': False, 

    # Options to pass into the consumer when running ``manage.py run_huey``
    'consumer_options': {'workers': 4},
}

MAIL_BOT_EMAIL = 'mailbot@fcs.com'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'syslog': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        }
    },
    'loggers': {
       'huey.consumer': {
            'handlers': ['syslog'],
            'level': 'INFO',
            'propagate': True,
       }
    }
}

