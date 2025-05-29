from pathlib import Path

import dj_database_url
import environ

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
    'corsheaders',
    'api',
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

ALLOWED_REDIRECT_URIS = [
    'http://localhost:3000/',  # React
    'http://127.0.0.1:3000/',  # React
    # 'https://twoja-web-aplikacja.pl/', # Adres produkcyjny
    'moja-apka://oauth/callback',  # Mobile scheme
]
