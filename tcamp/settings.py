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
AWS_PRELOAD_METDATA = True
AWS_HEADERS = {
    "Vary": "Accept-Encoding",
    "Cache-Control": "max-age=86400",
    "Expires": "Sat, 3 May 2020 00:00:00 GMT"
}
AWS_STORAGE_BUCKET_NAME = "assets.transparencycamp.org"
S3_URL = 'http://assets.transparencycamp.org.s3.amazonaws.com/%s/' % ASSET_SITE_VERSION

COMPRESS_STORAGE = 's3utils.StaticRootS3BotoStorage'
COMPRESS_ROOT = os.path.join(PROJECT_ROOT, 'static-cache')
COMPRESS_URL = S3_URL + 'static/'
COMPRESS_CSS_FILTERS = (
    'compressor.filters.cssmin.CSSMinFilter',
    'compressor.filters.css_default.CssAbsoluteFilter',
)
# COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_JS_FILTERS = (
    'compressor.filters.jsmin.JSMinFilter',
)

STATICFILES_STORAGE = COMPRESS_STORAGE
STATIC_ROOT = COMPRESS_ROOT
STATIC_URL = COMPRESS_URL

DEFAULT_FILE_STORAGE = 's3utils.MediaRootS3BotoStorage'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media-cache')
MEDIA_URL = S3_URL + 'media/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/logged-in/'
LOGOUT_URL = '/logout/'
GOOGLEAUTH_DOMAIN = 'sunlightfoundation.com'
GOOGLEAUTH_IS_STAFF = True
GOOGLEAUTH_GROUPS = ('staff', )
GOOGLEAUTH_REALM = 'transparencycamp.org'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
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
    "camp.context_processors.sponsors",
    "context_processors.basic_settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'middleware.ConditionalSessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'middleware.ConditionalCsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.ConditionalAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.ConditionalMessageMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'pages.middleware.PagesMiddleware',
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
    'django.contrib.humanize',
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
    'sfapp',
    'herokal',

    'django_extensions',
    'debug_toolbar',
    'django_pdb',
    'template_repl',
    'gunicorn',
    'varnishapp',
    'raven.contrib.django.raven_compat',

    'api',
    'brainstorm',
    'pages',
    'sked',
    'camp',
    'sms',
    'twit',
)

VARNISH_WATCHED_MODELS = (
    'sked.event',
    'sked.session',
    'pages.page',
    'brainstorm.subsite',
    'brainstorm.idea',
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
            'level': 'INFO',
        },
    }
}

from herokal.settings import *
