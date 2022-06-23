import base64, os, sys
from functools import wraps
from flask import request
from app.models.user import User

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
            print('@cred error', e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            tb = e.__traceback__
            print(tb.tb_lasti)
            return 'Internal error', 500
    return wrapper

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('auth')
        if not token:
            return {'error': 'No token provided'}, 401
        user = User.check_token(token)['user']
        res = User.check_token(token)['res']
        if res == 'expired':
            return {'error': 'expired token'}, 401
        elif res == 'bad':
            return {'error': 'invalid token'}, 401
        elif not user:
            return {'error': 'invalid token'}, 401
        return f(*args, **kwargs, user = user)
    return wrapper