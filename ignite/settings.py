"""
Django settings for ignite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# configuration settings
from conf import PROJECT_DIR, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from conf import IGNITE_IP, IGNITE_PORT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.join(os.getcwd(), PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hr-)vj6q4r&z&wojg58&$!_#4r_ge@uzgqw!cnec@vdeucy)pl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # REST
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'djoser',

    # Ignite Apps
    'administration',
    'bootstrap',
    'config',
    'discovery',
    'fabric',
    'feature',
    'group',
    'image',
    'pool',
    'switch',
    'workflow',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Ignite Middleware
    'middleware.tokenexpire.TokenExpiredMiddleware',
    'middleware.logout.LogoutMiddleWare',
    'middleware.exception.ExceptionMiddleware',
    'middleware.crossdomainxhr.XsSharing',
    'middleware.logger.LoggingMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'middleware.radius.RadiusBackend',
    'middleware.tacacs.TacacsBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'ignite.urls'

WSGI_APPLICATION = 'ignite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
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


# Djoser

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}


# CORS

XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*', 'Authorization', 'X-CSRFToken']

#UI directory
UI_ROOT = os.path.join(BASE_DIR, "webapp/dist")

# Media Root
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Scripts Path
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts/")

# Packages Path
PKG_PATH = os.path.join(SCRIPT_PATH, "packages/")

#Repository path
REPO_PATH = os.path.join(MEDIA_ROOT, "repo/")

#Switch config path
SWITCH_CONFIG_PATH = os.path.join(MEDIA_ROOT, "switch/")

# External packages
YAML_LIB = "PyYAML-3.11.tar"

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'ignite/ignite.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
        },
        'administration': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'bootstrap': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'config': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'discovery': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'fabric': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'feature': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'group': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'image': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'pool': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'switch': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'utils': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'workflow': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}


# Swagger settings

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
    'base_path': IGNITE_IP + ':' + IGNITE_PORT + '/docs',
    'info': {
        'contact': '',
        'description': '',
        'license': 'Apache 2.0',
        'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'termsOfServiceUrl': '',
        'title': 'Ignite REST API documentation',
    },
    'doc_expansion': 'none',
}
