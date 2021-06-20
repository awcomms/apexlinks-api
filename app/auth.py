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

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return '', 401
        user = User.check_token(token)
        if not user:
            return '', 401
        return f(*args, **kwargs, user=user)
    return wrapper
