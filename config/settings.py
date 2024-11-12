import sys
from datetime import timedelta
from pathlib import Path

import environ

root = environ.Path(__file__) - 2
env = environ.Env()
environ.Env.read_env(env.str(root(), '.env'))

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env.str('SECRET_KEY', default='!!!SET DJANGO_SECRET_KEY!!!',)
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='127.0.0.1').split(' ')
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party packages
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_extensions',
    'djangoviz',
    'phonenumber_field',
    'ckeditor',
    'ckeditor_uploader',
    'django_bleach',
    'django_celery_results',

    # Apps
    'api.apps.ApiConfig',
    'common.apps.CommonConfig',
    'users.apps.UsersConfig',
    'blog.apps.BlogConfig',
    'rating.apps.RatingConfig',
    'subscription.apps.SubscriptionConfig',

    # After apps
    'drf_spectacular',
    'djoser',
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
    'common.middlewares.ckeditor.CKEditorPostMiddleware'
]

# Debug settings
if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INTERNAL_IPS = [
        "127.0.0.1",
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: bool(request.headers.get('x-requested-with') != 'XMLHttpRequest'),
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
            'KEY_PREFIX': 'blog_dev',
            'TIMEOUT': 60 * 1,  # 1 min
        }
    }
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = True if not DEBUG else False
SESSION_COOKIE_SECURE = True if not DEBUG else False
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

DATABASES = {
    "default": {
        "ENGINE": env.str('SQL_ENGINE', 'django.db.backends.sqlite3'),
        "NAME": env.str('SQL_DB', BASE_DIR / 'db.sqlite3'),
        "USER": env.str('SQL_USER', 'user'),
        "PASSWORD": env.str('SQL_PASSWORD', 'password'),
        "HOST": env.str('SQL_HOST', 'localhost'),
        "PORT": env.int('SQL_PORT', 5432),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ['users.backends.AuthBackend']
LOGIN_REDIRECT_URL = 'blog:index'
LOGOUT_REDIRECT_URL = 'blog:index'

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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# CACHE
if not DEBUG:
    REDIS_PASSWORD = env.str('REDIS_PASSWORD', default='!!!SET REDIS_PASSWORD!!!')
    REDIS_HOST = env.str('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = env.str('REDIS_PORT', '6379')
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}',
            'KEY_PREFIX': 'blog',
            'TIMEOUT': 60 * 15,  # 15 min
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'minib.log',
            'formatter': 'verbose',
            'backupCount': 2,
            'maxBytes': 1024 * 1024 * 5,  # 5MB
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

######################
# LOCALIZATION
######################
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

######################
# STATIC AND MEDIA
######################
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

###########################
# e-mail configuration
###########################
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'sender_email@gmail.com'
# EMAIL_HOST_PASSWORD = 'app-password'
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False


###########################
# CKEditor & django-bleach
###########################
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_FORCE_JPEG_COMPRESSION = True
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', ],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['Smiley', 'SpecialChar'], ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
        'extraPlugins': 'justify,liststyle,indent',
        'height': 450,
    },
    'comments': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Undo', 'Redo'],
            ['Link', 'Unlink'],
            ['NumberedList', 'BulletedList'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Maximize'],
            ['Source'],
        ],
        'extraPlugins': 'justify,liststyle',
        'height': 200,
    },
}

BLEACH_ALLOWED_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                       'table', 'thead', 'tbody', 'tr', 'th', 'td', 'blockquote', 'hr', 'br',
                       'p', 'b', 'i', 'u', 'em', 's', 'strong', 'a', 'img', 'code',
                       'ul', 'ol', 'li']
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'src', 'alt',
                             'border', 'cellspacing', 'cellpadding', 'colspan', 'rowspan']

# Assuming style is an allowed attribute
BLEACH_ALLOWED_STYLES = ['font-family', 'font-weight', 'text-decoration', 'font-variant', 'width']
BLEACH_STRIP_TAGS = True
BLEACH_STRIP_COMMENTS = True
BLEACH_DEFAULT_WIDGET = 'ckeditor.widgets.CKEditorWidget'

###########################
# CELERY
###########################
# For docker. Take a note, that @rabbit should be the name of the service we use for the RabbitMQ container in compose
RABBITMQ_DEFAULT_USER = env.str("RABBITMQ_DEFAULT_USER", default='guest')
RABBITMQ_DEFAULT_PASS = env.str("RABBITMQ_DEFAULT_PASS", default='guest')
CELERY_BROKER_URL = f'amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@rabbit//'

# For local development
# CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'

CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_RESULT_EXPIRES = 18000

# For development on windows
# CELERY_WORKER_POOL = 'solo'

###########################
# REST FRAMEWORK
###########################
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'api.spectacular.renderers.OnlyRawBrowsableAPIRenderer',  # Disable rendering HTML form for endpoints
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5,
}

######################
# CORS HEADERS
# https://pypi.org/project/django-cors-headers/
######################
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']

######################
# DRF SPECTACULAR
######################
# Let's read SPECTACULAR description from a file.
SPECTACULAR_DESCRIPTION_PATH = BASE_DIR / 'config' / 'spectacular-description.md'
SPECTACULAR_DESCRIPTION = SPECTACULAR_DESCRIPTION_PATH.read_text(encoding='utf-8')

SPECTACULAR_SETTINGS = {
    'TITLE': 'Blog app',
    'DESCRIPTION': SPECTACULAR_DESCRIPTION,
    'VERSION': '1.0.0',

    'SERVE_AUTHENTICATION': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication'
    ],
    'SWAGGER_UI_SETTINGS': {
        'DeepLinking': True,
        'DisplayOperationId': True,
        'persistAuthorization': True
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

#######################
# DJOSER
#######################
DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {},
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=360),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=1),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

######################
# TEST SETTINGS
######################
TESTING = 'test' in sys.argv
if TESTING:
    DEBUG_TOOLBAR_CONFIG = {
        'IS_RUNNING_TESTS': False,
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'ERROR',
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    }
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
