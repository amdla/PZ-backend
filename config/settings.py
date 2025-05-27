from pathlib import Path

import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(env_file=BASE_DIR / '.env')

SECRET_KEY = env("SECRET_KEY")
USOS_CONSUMER_KEY = env('Consumer_Key') 
USOS_CONSUMER_SECRET = env('Consumer_Secret')

DEBUG = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/oauth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # You can add project-level template directories here if you have any
            # e.g., os.path.join(BASE_DIR, 'templates')
        ],
        # APP_DIRS must be True for Django to find templates within installed applications
        # like Django Rest Framework's 'rest_framework/api.html'
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Applications
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'api',
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'config.urls'

ALLOWED_HOSTS = ['0.0.0.0', 'localhost']

# Database configuration
DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}