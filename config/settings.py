from pathlib import Path

import environ
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(env_file=BASE_DIR / '.env')

SECRET_KEY = env("SECRET_KEY")
USOS_CONSUMER_KEY = '' # for local testing hard code the keys here
USOS_CONSUMER_SECRET = ''

DEBUG = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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