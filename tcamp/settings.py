import os
import re
import json
import sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

GRAPPELLI_ADMIN_TITLE = "TransparencyCamp"
AUTOCOMPLETE_LIMIT = 5

# This determines which folder static assets and media will be written to on S3.
ASSET_SITE_VERSION = '3.0'
AWS_QUERYSTRING_AUTH = False
AWS_S3_SECURE_URLS = False
AWS_STORAGE_BUCKET_NAME = "assets.transparencycamp.org"
S3_URL = 'http://assets.transparencycamp.org.s3.amazonaws.com/%s/' % ASSET_SITE_VERSION
COMPRESS_URL = S3_URL + 'static/'
DEFAULT_FILE_STORAGE = 's3utils.MediaRootS3BotoStorage'
COMPRESS_STORAGE = 's3utils.StaticRootS3BotoStorage'
STATICFILES_STORAGE = COMPRESS_STORAGE
STATIC_ROOT = os.path.join(PROJECT_ROOT, '.static')
STATIC_URL = COMPRESS_URL
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '.media')
MEDIA_URL = S3_URL + 'media/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/logged-in/'
LOGOUT_URL = '/logout/'
GOOGLEAUTH_DOMAIN = 'sunlightfoundation.com'
GOOGLEAUTH_IS_STAFF = True
GOOGLEAUTH_GROUPS = ('staff', )
GOOGLEAUTH_REALM = 'transparencycamp.org'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'pages.templateloader.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "treenav.context_processors.treenav_active",
    "social.apps.django_app.context_processors.backends",
    "social.apps.django_app.context_processors.login_redirect",
    "sked.context_processors.current_event",
    "brainstorm.context_processors.brainstorm",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'pages.middleware.PagesMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'googleauth.backends.GoogleAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.github.GithubOAuth2',
    'social.backends.disqus.DisqusOAuth2',
)

EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grappelli',
    'django.contrib.admin',
    # 'django.contrib.admindocs',

    'south',
    'compressor',
    'storages',
    'taggit',
    'markdown_deux',
    'markitup',
    'reversion',
    'mptt',
    'treenav',
    'social.apps.django_app.default',
    'tastypie',
    'djutils',
    'django_twilio',

    'django_extensions',
    'debug_toolbar',
    'django_pdb',
    'template_repl',
    'gunicorn',

    # 'api',
    'brainstorm',
    'pages',
    'sked',
    'camp',
    'sms',
    'twit',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'sql': {
            'format': '%(levelname)s %(message)s %(duration)s, %(params)s %(sql)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }
}

if 'DEBUG' in os.environ.keys():
    # Load .env file and
    # Parse database configuration from $DATABASE_URL
    import dj_database_url
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config()
    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    for setting, value in os.environ.iteritems():
        if re.search(r'^[A-Z][A-Z0-9_]+$', setting):
            try:
                setattr(sys.modules[__name__], setting, json.loads(value))
            except:
                setattr(sys.modules[__name__], setting, value)
else:
    try:
        from local_settings import *
    except ImportError, e:
        print """Caught %s trying to import local_settings. Please make sure
                 local_settings.py exists and is free of errors.
              """
        raise
