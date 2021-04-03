"""
Django settings for CenterStage project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env_path = Path(BASE_DIR) / '.env'
load_dotenv(dotenv_path=env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z(3*uqch79bmakbwp1g&#k&#ik%!g(r!bzk_6vnooi!#4y-&b8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if sys.platform == "win32" or os.getenv('DEPLOY_ENV') else False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'phonenumber_field',
    'corsheaders',

    # project specific apps
    'frontend',
    'users',
    'engine',
    'notifications',
    'zoom'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'CenterStage.middleware.general_checks.CheckOnboarding',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'CenterStage.urls'

API_URL = '/api'
TEACHER_TEMPLATES_PATH = '/teacher'
LESSON_PAGES_PATH = "/lesson"
STUDENT_TEMPLATES_PATH = '/student'
CENTERSTAGE_STATIC_PATH = "/centrestage"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'notifications', 'email_templates')
        ],
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

WSGI_APPLICATION = 'CenterStage.wsgi.application'

if sys.platform == "win32" or os.environ.get("DEPLOY_ENV", "PROD") == "DEV":
    SCHEME = 'http'
    SITE_URL = 'localhost:8000'
    BASE_URL = '{}://{}'.format(SCHEME, SITE_URL)
    SESSION_COOKIE_DOMAIN = 'localhost'
else:
    SCHEME = 'https'
    SITE_URL = 'centrestage.live'
    BASE_URL = '{}://{}'.format(SCHEME, SITE_URL)

SESSION_COOKIE_DOMAIN = SITE_URL
SESSION_COOKIE_SECURE = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if sys.platform == "win32" or os.environ.get("DEPLOY_ENV", "PROD") == "DEV":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'centerstage',
            'USER': 'postgres',
            'PASSWORD': 'root12345',
            'HOST': 'localhost',
            'PORT': 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'centerstage',
            'USER': os.environ.get("DB_USER"),
            'PASSWORD': os.environ.get("DB_PASSWORD"),
            'HOST': os.environ.get("DB_HOST"),
            'PORT': 5432,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# Caching
if sys.platform == "win32" or os.getenv('DEPLOY_ENV'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'KEY_PREFIX': 'centerstage'
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
            'KEY_PREFIX': 'centerstage'
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False  # Temporary Set to False on Jan 26 for ZoomMeetingAPIView

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# setting user model to custom user model
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.BearerAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

"""
Swagger Settings
"""
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
    },
    'LOGIN_URL': '/api/login',
}

REDOC_SETTINGS = {
   'LAZY_RENDERING': False,
}


"""
Settings for AWS account
"""
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")

AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")

AWS_S3_SIGNATURE_VERSION = 's3v4'

AWS_S3_REGION_NAME = 'us-east-1'

AWS_DEFAULT_ACL = None

# Twilio sms notifications settings
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

# sendgrid settings to send email
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Zoom settings
ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
ZOOM_REDIRECT_URL = os.environ.get("ZOOM_REDIRECT_URL")

# Temporary storage for the file upload
if sys.platform == "win32":
    TEMP_DIR = Path(BASE_DIR) / "tmp_files"
else:
    TEMP_DIR = Path("/tmp") / "tmp_files"

os.makedirs(TEMP_DIR, exist_ok=True)

if sys.platform == "win32":
    pass
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(name)s : %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
            },
            'CenterStageLogs': {
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1024*1024*5,  # 5 MB
                'backupCount': 5,
                'formatter': 'simple',
                'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
                'level': 'ERROR',
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'engine': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'frontend': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'notifications': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'payments': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'users': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            },
            'zoom': {
                'handlers': ['console', 'CenterStageLogs'],
                'level': 'ERROR' if str.upper(os.getenv("DEPLOY_ENV", "production")) == 'PRODUCTION' else 'INFO',
                'propagate': True,
            }
        }
    }
