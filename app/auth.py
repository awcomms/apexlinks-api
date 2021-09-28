import base64
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
        except:
            return {'error': 'something wrong with your credentials'}
    return wrapper

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('auth')
        print('token', token)
        if not token:
            print('no token')
            return {'error': 'No token provided'}, 401

        user = User.check_token(token)
        
        if not user:
            print('invalid token')
            return {'error': 'Invalid token', 'invalid': True}, 401
        else:
            return f(*args, **kwargs)
    return wrapper