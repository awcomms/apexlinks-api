from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from flask import make_response
from flask import request
from app import db
from app.user_model import User
from app.api import bp

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
    body = {'user': user.dict()}
    return make_response(body, headers)

@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    if user:
        user.token = None
        db.session.commit()
    return '', 202