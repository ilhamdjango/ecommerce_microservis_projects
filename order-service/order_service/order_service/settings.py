from pathlib import Path
from dotenv import load_dotenv

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv() 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-test-key-for-development-12345')

# ALLOWED_HOSTS problemini həll et  
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "ecommerce-order-service-a9fh.onrender.com",
    "ecommerce-order",  # 👈 Docker konteyner adı
    "0.0.0.0",
    "*",  # 👈 TEST ÜÇÜN
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://ecommerce-order-service-a9fh.onrender.com",
]

# Cors settings
CORS_ALLOW_ALL_ORIGINS = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'drf_yasg',
    # Apps
    'orders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'order_service.wsgi.application'


# Database(PostgreSQL) configuration

# Check if running on Cloud Run
is_cloud_run = os.environ.get("RUNNING_ON_CLOUDRUN", "").lower() == "true"

if is_cloud_run:
    # Cloud Run configuration with Cloud SQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': f"/cloudsql/{os.environ.get('CLOUD_SQL_CONNECTION_NAME')}",
            'PORT': '',
        }
    }
else:
    # Local development configuration - SADƏLƏŞDİRİLMİŞ
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'ecommerce_db'),
            'USER': os.getenv('POSTGRES_USER', 'ecommerce_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', '12345'),
            'HOST': os.getenv('POSTGRES_HOST', 'db-order'),  # 👈 db-order
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
    # Local development configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'URL': os.getenv('DATABASE_URL', 'postgresql://test:LqjnHzmC9VbGU2nfBjiv6G3yYXgVPOT1@dpg-d3oum9p5pdvs73a7dtug-a/order_service_1ook'),
            'NAME': os.getenv('POSTGRES_DB', 'order_service_1ook'),
            'USER': os.getenv('POSTGRES_USER', 'postgre'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'LqjnHzmC9VbGU2nfBjiv6G3yYXgVPOT1'),
            'HOST': os.getenv('POSTGRES_HOST', 'dpg-d3oum9p5pdvs73a7dtug-a'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': 600,  
            'OPTIONS': {
                'sslmode': 'disable',
            },
        
       
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Media / Static configuration

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'order_service/media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# RestFramework settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Swagger settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'My Project API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
}

print(f"🚀 Django starting... Debug={DEBUG}, Port={os.getenv('PORT')}")

#Rabbit MQ
CELERY_BROKER_URL = 'amqps://cxssijuj:MHbrwwU43FaDiUCiW7efAy-_BMuVwgiE@seal.lmq.cloudamqp.com/cxssijuj'
CELERY_RESULT_BACKEND = 'rpc://'  # optional, nəticəni saxlamaq üçün
