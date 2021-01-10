import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    ORIGINS = os.environ.get('ORIGINS')
    PAYSTACK = os.environ.get('PAYSTACK')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    SECRET_KEY='dev'
    USERS_PER_PAGE = 10
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL') or \
        'http://localhost:9200'
    FRONT_END = os.environ.get('FRONT_END')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:love@localhost:5432/marketlinks'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    LANGUAGES = ['en', 'es']
    USERS_PER_PAGE = 10
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_EMAIL = 'edge3769@gmail.com'
    MAIL_PASSWORD = 'loveGM1!'
    ADMINS = ['edge2347@gmail.com']
    JWT_HEADER_TYPE = ''
    JWT_ACCESS_TOKEN_EXPIRES = False