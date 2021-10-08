import os
from dotenv import load_dotenv

db_uri = os.environ.get('DATABASE_URL') or 'postgresql://postgres:love@localhost:5432/apexlinks'

class Config(object):
    PAYSTACK_TEST = os.environ.get('PAYSTACK_TEST')
    PAYSTACK_TEST_KEY = os.environ.get('PAYSTACK_TEST_KEY')
    PAYSTACK_LIVE_KEY = os.environ.get('PAYSTACK_LIVE_KEY')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    SECRET_KEY= os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_DATABASE_URI = db_uri.replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    LANGUAGES = ['en', 'es']
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp-mail.outlook.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'apexlinks1@outlook.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'svelte37'
    ADMINS = ['apexlinks1@outlook.com', 'edge3769@gmail.com']
    JWT_HEADER_TYPE = ''
    JWT_ACCESS_TOKEN_EXPIRES = False