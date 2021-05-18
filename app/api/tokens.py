from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from flask import make_response
from flask import request
from app import db
from app.user_model import User
from app.api import bp

@bp.route('/users/<value>', methods=['GET'])
def get_user(value):
    # try:
    #     token = request.headers.get('Token')
    #     user = User.query.filter_by(token=token).first()
    #     if user:
    #         return user.dict()
    try:
        user = User.query.get(int(value))
    except:
        user = User.query.filter_by(username=value).first()
    if not user:
        return '', 404
    return user.dict()

@bp.route('/user', methods=['GET'])
def user():
    token = request.headers.get('Token')
    user = User.query.filter_by(token=token).first()
    if user:
        return user.dict()
    else:
        return '', 401

@bp.route('/tokens', methods=['POST'])
def get_token():
    q = request.get_json()
    headers = Headers()
    headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
    username = q['username']
    password = q['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            'usernameInvalid': True,
            'usernameError': 'User does not exist'
        }
    if not user.check_password(password):
        return {
            'passwordInvalid': True,
            'passwordError': 'Wrong password'
        }
    user.token = create_access_token(identity=username)
    db.session.commit()
    body = {'token': user.token}
    return make_response(body, headers)

@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    token = request.headers.get('Token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    if user:
        user.token = None
        db.session.commit()
    return '', 202