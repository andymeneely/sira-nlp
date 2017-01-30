import os
import multiprocessing
import sys

ENVIRONMENT = os.environ.get('ENV', 'DEV')
if ENVIRONMENT not in ['DEV', 'TEST', 'PROD']:
    raise Exception('{} is an unknown environment'.format(ENVIRONMENT))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ENVIRONMENT == 'PROD':
    DATA_DIR = '/home/artifacts/linsights/'
elif ENVIRONMENT == 'DEV':
    DATA_DIR = os.path.join(BASE_DIR, 'app/data')
elif ENVIRONMENT == 'TEST':
    DATA_DIR = os.path.join(BASE_DIR, 'app/tests/data')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

try:
    from linsights import dbsettings
    DATABASES = dbsettings.get(ENVIRONMENT)
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

# Paths
BUGS_PATH = os.path.join(DATA_DIR, 'bugs/{year}')
IDS_PATH = os.path.join(DATA_DIR, 'ids')
REVIEWS_PATH = os.path.join(DATA_DIR, 'reviews/{year}')
VULNERABILITIES_PATH = os.path.join(DATA_DIR, 'vulnerabilities')
NLP_CACHE_PATH = os.path.join(DATA_DIR, 'nlp')

# Preferences

# Years for which data is available
YEARS = list(range(2008, 2017))

# Addresses of bots that post messages during a code review
BOTS = ['commit-bot@chromium.org']

# Types of files that are considered from vulnerability-fixing code reviews
FILETYPES_WHITELIST = [
        '.c', '.cc', '.cpp', '.gyp', '.h', '.js', '.make', 'Makefile', '.py',
        '.S', '.sb', '.scons', '.sh'
    ]

# Number of processes to use when parallel processing
CPU_COUNT = multiprocessing.cpu_count()

# Maximum number of items in a queue
QUEUE_SIZE = 5000
