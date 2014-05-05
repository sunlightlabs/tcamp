DEBUG = True
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS
INTERNAL_IPS = ('127.0.0.1', )
SECRET_KEY = ''
DATABASES = {
    'local': {
        'ENGINE': '',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'staging': {
        'ENGINE': '',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'production': {
        'ENGINE': '',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DATABASES['default'] = DATABASES['local']

FAVICON = ''
APPLE_TOUCH_ICON = ''
SHARING_IMAGE = ''
FB_APP_ID = ''
GOOGLE_ANALYTICS_ID = ''

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
ASSET_SITE_VERSION = '1.0'
COMPRESS_URL = ''
COMPRESS_STORAGE = ''
STATICFILES_STORAGE = COMPRESS_STORAGE
STATIC_URL = COMPRESS_URL

POSTMARK_API_KEY = ''
POSTMARK_SENDER = ''

GOOGLEAUTH_DOMAIN = ''
GOOGLEAUTH_REALM = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''
GOOGLE_OAUTH2_CLIENT_ID = ''
GOOGLE_OAUTH2_CLIENT_SECRET = ''
GITHUB_APP_ID = ''
GITHUB_API_SECRET = ''
DISQUS_CLIENT_ID = ''
DISQUS_CLIENT_SECRET = ''
AKISMET_KEY = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_KEY = ''
TWITTER_ACCESS_SECRET = ''

DISQUS_SHORTNAME = ''
BRAINSTORM_USE_DISQUS = True
BRAINSTORM_LOGIN_OPTIONS = (
    ('Twitter', '/login/twitter/'),
    ('Facebook', '/login/facebook/'),
    ('Google', '/login/google-oauth2/'),
    ('Github', '/login/github/'),
)

VARNISH_MANAGEMENT_ADDRS = ()

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''

RAVEN_CONFIG = {
    'dsn': '',
}

SLACK_TOKEN = ''
