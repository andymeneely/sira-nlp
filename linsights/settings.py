import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '#cmj@ekvxqjysua*+49&f-erlf$avg@$8hppv^8i=9g+86(j8a'
DEBUG = False
INSTALLED_APPS = ['app']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Application Settings
DATA_PATH = os.path.join(BASE_DIR, 'app/data')
if os.environ.get('ENV') == 'PROD':
    DATA_PATH = '/tmp/linsights/data'

IDS_PATH = os.path.join(DATA_PATH, 'ids')
REVIEWS_PATH = os.path.join(DATA_PATH, 'reviews/{year}')
BOTS = ['commit-bot@chromium.org']
