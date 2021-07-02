import base64
from functools import wraps
from flask import request
from app.user_model import User

def cred(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        s = request.headers.get('auth')
        s = s.encode('ascii')
        s = base64.b64decode(s)
        s = s.decode('ascii')
        s = s.split(':')
        username = s[0]
        password = s[1]
        return f(*args, **kwargs, username=username, password=password)
    return wrapper

def auth(optional=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get('token')
            user = None
            if not optional and not token:
                return '', 401
            try:
                user = User.check_token(token)
            except:
                if not optional:
                    return {'error': 'invalid token'}, 423
            if not optional and not user:
                return '', 401
            return f(*args, **kwargs, user=user)
        return wrapper
    return decorator
