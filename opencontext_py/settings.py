"""
Django settings for opencontext_py project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

# The following reads secret settings from a JSON file called 'secrets.json'
import json
import os.path
from os.path import abspath, basename, dirname, join, normpath
from django.core.exceptions import ImproperlyConfigured

if os.path.isfile('secrets.json'):
    # get secret configuration information from the secrets.json file
    with open('secrets.json') as f:
        secrets = json.loads(f.read())
else:
    # print('Trying ' + BASE_DIR + '/secrets.json')
    with open(BASE_DIR + '/secrets.json') as f:
        secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    """Get secret variable or return an exception"""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = 'Set the {0} environment variable'.format(setting)
        raise ImproperlyConfigured(error_msg)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY')
SOLR_HOST = get_secret('SOLR_HOST')
SOLR_PORT = get_secret('SOLR_PORT')
SOLR_COLLECTION = get_secret('SOLR_COLLECTION')

# SECURITY WARNING: don't run with debug turned on in production!
if get_secret('DEBUG') == 1:
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False




ALLOWED_HOSTS = ['.opencontext.org']

# saves configuration problems
# settings.py can be updated without upsetting
# local deployment configurations
added_host = get_secret('ALLOWED_HOST')
if len(added_host) > 1:
    ALLOWED_HOSTS.append(added_host)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    # 'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'opencontext_py.apps.edit.inputs.profiles',
    'opencontext_py.apps.edit.inputs.fieldgroups',
    'opencontext_py.apps.edit.inputs.inputfields',
    'opencontext_py.apps.edit.inputs.inputrelations',
    'opencontext_py.apps.edit.inputs.rules',
    'opencontext_py.apps.entities.uri',
    'opencontext_py.apps.entities.entity',
    'opencontext_py.apps.ocitems.namespaces',
    'opencontext_py.apps.ocitems.subjects',
    'opencontext_py.apps.ocitems.ocitem',
    'opencontext_py.apps.ocitems.manifest',
    'opencontext_py.apps.ocitems.assertions',
    'opencontext_py.apps.ocitems.events',
    'opencontext_py.apps.ocitems.geospace',
    'opencontext_py.apps.ocitems.mediafiles',
    'opencontext_py.apps.ocitems.documents',
    'opencontext_py.apps.ocitems.persons',
    'opencontext_py.apps.ocitems.projects',
    'opencontext_py.apps.ocitems.strings',
    'opencontext_py.apps.ocitems.octypes',
    'opencontext_py.apps.ocitems.octypetree',
    'opencontext_py.apps.ocitems.predicates',
    'opencontext_py.apps.ocitems.predicatetree',
    'opencontext_py.apps.ocitems.identifiers',
    'opencontext_py.apps.ocitems.obsmetadata',
    'opencontext_py.apps.imports.ocmysql',
    'opencontext_py.apps.imports.fields',
    'opencontext_py.apps.imports.fieldannotations',
    'opencontext_py.apps.imports.records',
    'opencontext_py.apps.imports.sources',
    'opencontext_py.apps.ldata.linkannotations',
    'opencontext_py.apps.ldata.linkentities',
    'opencontext_py.apps.exports.expfields',
    'opencontext_py.apps.exports.exprecords',
    'opencontext_py.apps.exports.exptables',
    'opencontext_py.apps.indexer',
    'opencontext_py.apps.searcher.sets',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # added caching
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)


ROOT_URLCONF = 'opencontext_py.urls'

WSGI_APPLICATION = 'opencontext_py.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret('DATABASES_NAME'),
        'USER': get_secret('DATABASES_USER'),
        'PASSWORD': get_secret('DATABASES_PASSWORD'),
        'HOST': get_secret('DATABASES_HOST')
    }
}

ADMINS = (
    (get_secret('ADMIN_NAME'), get_secret('ADMIN_EMAIL'))
)
MANAGERS = (
    (get_secret('MANAGE_NAME'), get_secret('MANAGE_EMAIL'))
)

# CACHES, Makes things faster
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'oc_cache_table',
        'TIMEOUT': 360,
        'OPTIONS': {
            'MAX_ENTRIES': 5000
        }
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ----------------------------
# IMPORTER SETIINGS
# ----------------------------
IMPORT_BATCH_SIZE = 500 # number of records to import in 1 batch


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
if DEBUG:
    ADMIN_MEDIA_PREFIX = '/static/admin/'
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR + '/static/'
    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
        '/static/',
    )
    STATIC_EXPORTS_ROOT = BASE_DIR + '/static/exports/'
else:
    ADMIN_MEDIA_PREFIX = '/static/admin/'
    STATIC_URL = '/static/'
    STATIC_ROOT = get_secret('STATIC_ROOT')
    STATICFILES_DIRS = (
        normpath(join(BASE_DIR, 'static')),
    )

import socket

#get the local host server name
try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

# assumes DEPLOYED_HOST starts with 'http://' or 'https://'
DEPLOYED_HOST = get_secret('DEPLOYED_HOST')
if 'http://' not in DEPLOYED_HOST and 'https://' not in DEPLOYED_HOST:
    DEPLOYED_HOST = 'http://' + DEPLOYED_HOST
DEPLOYED_SITE_NAME = get_secret('DEPLOYED_SITE_NAME')
if get_secret('DEPLOYED_HOST') == 1:
    TO_DEPLOYED_URIS = True
else:
    TO_DEPLOYED_URIS = False

CANONICAL_HOST = 'http://opencontext.org'
CANONICAL_SITENAME = 'Open Context'

# useful hack to allow presence of a 'debug.json' file to
# toggle debug mode
if os.path.isfile('debug.json'):
    # get secret configuration information from the secrets.json file
    DEBUG = True
    TEMPLATE_DEBUG = True
    DEPLOYED_HOST = 'http://localhost'
elif os.path.isfile(BASE_DIR + '/debug.json'):
    DEBUG = True
    TEMPLATE_DEBUG = True
    DEPLOYED_HOST = 'http://localhost'
else:
    # do nothing, no debug file flag
    pass


ITEM_TYPES = (
    ('subjects', 'subjects'),
    ('media', 'media'),
    ('documents', 'documents'),
    ('projects', 'projects'),
    ('persons', 'persons'),
    ('types', 'types'),
    ('predicates', 'predicates'),
    ('tables', 'tables'),
    ('vocabularies', 'vocabularies'),
)

SLUG_TYPES = ['predicates', 'projects']

STABLE_ID_URI_PREFIXES = {'doi': 'http://dx.doi.org/',
                          'orcid': 'http://orcid.org/',
                          'ark': 'http://n2t.net/ark:/'}

NAV_ITEMS = [{'key': 'about',
              'link': None,
              'display': 'About',
              'always': True,
              'urls': [{'display': 'About Open Context',
                        'link': '/about/'},
                       {'display': 'Uses',
                        'link': '/about/uses'},
                       {'display': 'Publishing',
                        'link': '/about/publishing'},
                       {'display': 'Grant Seekers',
                        'link': '/about/estimate'},
                       {'display': 'Concepts',
                        'link': '/about/concepts'},
                       {'display': 'Technology',
                        'link': '/about/technology'},
                       {'display': 'APIs and Web Services',
                        'link': '/about/services'},
                       {'display': 'Recipes using APIs',
                        'link': '/about/recipes'}]},
             {'key': 'explore',
              'link': None,
              'display': 'Explore',
              'always': True,
              'urls': [{'display': 'Browse Data Records',
                        'link': '/sets/'},
                       {'display': 'Browse Projects',
                        'link': '/projects/'}]},
             {'key': 'subjects',
              'link': '/subjects/',
              'display': 'Data Record',
              'always': False,
              'urls': None},
             {'key': 'media',
              'link': '/media/',
              'display': 'Media Item',
              'always': False,
              'urls': None},
             {'key': 'documents',
              'link': '/documents/',
              'display': 'Document Item',
              'always': False,
              'urls': None},
             {'key': 'persons',
              'link': '/persons/',
              'display': 'Person or Organization',
              'always': False,
              'urls': None},
             {'key': 'predicates',
              'link': '/predicates/',
              'display': 'Property or Relation',
              'always': False,
              'urls': None},
             {'key': 'types',
              'link': '/types/',
              'display': 'Category or Type',
              'always': False,
              'urls': None},
             {'key': 'tables',
              'link': '/tables/',
              'display': 'Data Table',
              'always': False,
              'urls': None},
             {'key': 'vocabularies',
              'link': '/vocabularies/',
              'display': 'Vocabulary / Ontology',
              'always': False,
              'urls': None}]

LOGGING_DIR = BASE_DIR + '/logs/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGING_DIR, 'error.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10
            }
        },
    'loggers': {
        'opencontext_py.apps.indexer.crawler': {
            'handlers': ['file'],
            'level': 'DEBUG'
            }
        }
    }
