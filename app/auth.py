import base64, os, sys
from functools import wraps
from flask import request
from app.user_model import User

def cred(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            s = request.headers.get('auth')
            s = s.encode('ascii')
            s = base64.b64decode(s)
            s = s.decode('ascii')
            s = s.split(':')
            username = s[0]
            password = s[1]
            return f(*args, **kwargs, username=username, password=password)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            tb = e.__traceback__
            print(tb.tb_lasti)
            return {'error': 'something wrong with your credentials'}
    return wrapper

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('auth')
        if not token:
            print('no token')
            return {'error': 'No token provided'}, 401
        user = User.check_token(token)
        if user:
            if user == 'expired':
                return {'error': 'expired token'}
            elif user == 'bad':
                return {'error': 'invalid token'}
            return f(*args, **kwargs, user = user)
        else:
            print('really invalid token: ', token)
            return {'error': 'invalid token', 'invalid': True}, 401
    return wrapper