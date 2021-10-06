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
def check_token(user=None):
    if user:
        if isinstance(user, str):
            return ({'error': user})
        return user.dict()

@bp.route('/tokens', methods=['POST'])
@cred
def get_token(username=None, password=None):
    print('tr', username, password)
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
    res = {
        'user': user.dict(),
        'token': user.get_token()
    }
    print('tr _be')
    return make_response(res, headers)

@bp.route('/tokens', methods=['DELETE'])
@auth
def revoke_token(user=None):
    user.token = None
    db.session.commit()
    return {}, 202