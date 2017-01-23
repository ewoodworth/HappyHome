"""Configuration for different environments."""
# pylint: disable=invalid-name
import os


class Config(object):

    """Base configuration."""

    SECRET_KEY = 'super-secret-key-that-needs-to-be-changed'
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13

    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
    SOCIAL_AUTH_USER_MODEL = 'flask_social_auth.user.models.User'
    SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
        'social.backends.google.GoogleOAuth2',
    )

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = (
        '953238239415-4mvdahlpba71b5c5aqphsva7pvt2qlto.apps.googleusercontent.com'
    )
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'ZxXGivUmSTYJuoV4j8pqgtUQ'


class DevConfig(Config):

    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    SOCIAL_AUTH_FACEBOOK_KEY = '1712779252282670'
    SOCIAL_AUTH_FACEBOOK_SECRET = '6e363707597ff8bbd369194eef8505f5'
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestConfig(Config):

    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False
