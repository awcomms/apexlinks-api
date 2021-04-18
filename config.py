import os
from dotenv import load_dotenv

class Config(object):
    PAYSTACK = os.environ.get('PAYSTACK')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    SECRET_KEY='dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://edge:edge@localhost:5432/apexlinks'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    LANGUAGES = ['en', 'es']
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_EMAIL = 'edge3769@gmail.com'
    MAIL_PASSWORD = 'loveGO1!'
    ADMINS = ['edge3769@gmail.com']
    JWT_HEADER_TYPE = ''
    JWT_ACCESS_TOKEN_EXPIRES = False