import os
from dotenv import load_dotenv
from pathlib import Path
from django.contrib.messages import constants as messages

# Загружаем переменные окружения из файла .env
load_dotenv()

# Указывает на текущую/корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секреты/ключ приложения
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# IP и домены, которые имеют доступ в приложение
ALLOWED_HOSTS = []


# Приложения для регистрации

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mailing',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

AUTH_USER_MODEL = 'users.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Настройки для базы данных

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #  имя вашей базы данных, получаемое из переменной окружения DATABASE_NAME
        'NAME': os.getenv('NAME', 'django_project'),
        # имя пользователя PostgreSQL, получаемое из переменной окружения DATABASE_USER
        'USER': os.getenv('USER', 'postgres'),
        # пароль пользователя PostgreSQL, получаемый из переменной окружения DATABASE_PASSWORD
        'PASSWORD': os.getenv('PASSWORD', 'postgres'),
        # адрес сервера базы данных, получаемый из переменной окружения DATABASE_HOST
        'HOST': os.getenv('HOST', 'localhost'),
        # порт, на котором работает PostgreSQL, обычно 5432, получаемый из переменной окружения DATABASE_PORT
        'PORT': os.getenv('PORT', '5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


MESSAGE_TAGS = {
    messages.SUCCESS: 'success',
}

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Путь директорий на диске, из которых мы загружаем статистические файлы
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


#после входа → на главную
LOGIN_REDIRECT_URL = '/'
#после выхода → на главную
LOGOUT_REDIRECT_URL = '/'



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@example.com'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}