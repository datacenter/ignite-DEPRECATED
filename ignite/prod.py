__author__  = "Rohit N Dubey"


"""
Django settings for ignite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from server_configuration import PROJECT_DIR, DBNAME, DBUSER, DBPASSWORD, DBHOST, DBPORT


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.getcwd() + PROJECT_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a&ck=fl4f253b(za-u79hc%ji0-75cin-!72l!ktol-5gg%2zi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = (
    # apps by django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_framework',
    'djoser',
    #User apps
    'configuration',
    'discoveryrule',
    'fabric_profile',
    'image_profile',
    'fabric',
    'pool',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.crossdomainxhr.XsSharing',
)

#XS_SHARING_ALLOWED_ORIGINS = ['http://127.0.0.1:8000','http://127.0.0.1:9010','http://localhost:9010']
#XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
#XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*', 'Authorization','X-CSRFToken']

# UI code
PROJECT_DIR = '/Ignite/ignite/'
UI_ROOT = BASE_DIR + '/dist'
#UI_ROOT = '/home/ignite/igniteml/Ignite/ignite/dist'
UI_URL = 'ui/'

ROOT_URLCONF = 'ignite.urls'

WSGI_APPLICATION = 'ignite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ignitedb',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DBNAME,                      # Or path to database file if using sqlite3.
        'USER': DBUSER,
        'PASSWORD': DBPASSWORD,
        'HOST': DBHOST,                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': DBPORT,                      # Set to empty string for default.
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'templates')
MEDIA_URL = '/configlets/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'ignite.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'configuration': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'pool': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'discoveryrule': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'fabric': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'ignite': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'fabric_profile': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'usermanagement': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'usermanagement.utils': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}
#DJANGO_LOG_LEVEL=DEBUG



SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'resource_access_handler': None,
    'base_path':'127.0.0.1:8000/docs',
    'info': {
        'contact': 'saleem.sheikh@maplelabs.com',
        'description': '',
        'license': 'Apache 2.0',
        'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'termsOfServiceUrl': 'http://127.0.0.1:8000/terms/',
        'title': 'Ignite REST API documentation',
    },
    'doc_expansion': 'none',
}
