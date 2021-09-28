from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from flask import make_response
from flask import request
from app.auth import cred
from app.auth import auth
from app import db
from app.user_model import User
from app.api import bp

@bp.route('/tokens')
@auth
def check_token():
    return {'ok': True}

@bp.route('/users/<value>', methods=['GET'])
def get_user(value):
    # try:
    #     token = request.headers.get('token')
    #     user = User.query.filter_by(token=token).first()
    #     if user:
    #         return user.dict()
    try:
        user = User.query.get(int(value))
    except:
        user = User.query.filter_by(username=value).first()
    if not user:
        return {}, 404
    return user.dict()

@bp.route('/user', methods=['GET'])
def user():
    token = request.headers.get('token')
    print('token', token)
    user = User.query.filter_by(token=token).first()
    if user:
        return user.dict()
    else:
        return {}, 401

@bp.route('/tokens', methods=['POST'])
@cred
def get_token(username=None, password=None):
    print(username, password)
    headers = Headers()
    headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            'error': True,
            'usernameInvalid': True,
            'usernameError': 'User does not exist'
        }, 400
    if not user.check_password(password):
        return {
            'error': True,
            'passwordInvalid': True,
            'passwordError': 'Wrong password'
        }, 400
    user.set_token()
    db.session.commit()
    res = {
        'user': user.dict(),
        'token': user.token
    }
    return make_response(res, headers)

@bp.route('/tokens', methods=['DELETE'])
@auth
def revoke_token(user=None):
    user.token = None
    db.session.commit()
    return {}, 202