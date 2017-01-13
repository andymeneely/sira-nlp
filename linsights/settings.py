import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

try:
    from linsights import dbsettings
    DATABASES = dbsettings.get()
except ImportError:
    pass

SECRET_KEY = '#cmj@ekvxqjysua*+49&f-erlf$avg@$8hppv^8i=9g+86(j8a'
DEBUG = False
INSTALLED_APPS = ['app']
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Application Settings

# Years for which data is available
YEARS = list(range(2008, 2017))

# Paths to various directories in which the data files are stored
DATA_PATH = os.path.join(BASE_DIR, 'app/data')
if os.environ.get('ENV') == 'PROD':
    DATA_PATH = '/tmp/linsights/data'

IDS_PATH = os.path.join(DATA_PATH, 'ids')
BUGS_PATH = os.path.join(DATA_PATH, 'bugs/{year}')
REVIEWS_PATH = os.path.join(DATA_PATH, 'reviews/{year}')
VULNERABILITIES_PATH = os.path.join(DATA_PATH, 'vulnerabilities')
BOTS = ['commit-bot@chromium.org']
FILETYPES_WHITELIST = [
    '.c', '.cc', '.cpp', '.gyp', '.h', '.js', '.make', 'Makefile', '.py', '.S',
    '.sb', '.scons', '.sh'
]
