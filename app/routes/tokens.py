from werkzeug.datastructures import Headers
from flask import make_response
from flask import request
from app.auth import cred
from app.auth import auth
from app import db
from app.models.user import User
from app.routes import bp


@bp.route('/tokens')
@auth
def check_token(user=None):
    if user:
        if isinstance(user, str):
            return ({'error': user})
        return user.dict()


@bp.route('/tokens', methods=['POST'])
@cred
def create_token(username=None, password=None):
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

    if password:
        if user.no_password:
            return {
                'error': True,
                'passwordInvalid': True,
                'passwordError': 'Wrong'
            }, 401
        if not user.check_password(password):
            return {
                'error': True,
                'passwordInvalid': True,
                'passwordError': 'Wrong password'
            }, 401
    else:
        if not user.no_password:
            return {
                'error': True,
                'passwordInvalid': True,
                'passwordError': 'Empty'
            }, 401
    res = {
        'user': user.dict(),
        'token': user.get_token()
    }
    print('success')
    return make_response(res, headers)

@bp.route('/tokens', methods=['DELETE'])
@auth
def revoke_token(user=None):
    user.token = None
    db.session.commit()
    return {}, 202
