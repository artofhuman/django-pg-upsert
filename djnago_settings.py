import sys
import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_PATH + '/tests/')

SECRET_KEY = 1

INSTALLED_APPS = [
    'tests.starwars',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_db',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'PASSWORD': "123456"
    }
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
]
