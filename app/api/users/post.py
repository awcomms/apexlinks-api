from flask import request
from app.api import bp
from app.auth import cred
from app.user_model import User
from app.misc import check_email

@bp.route('/users', methods=['POST'])
@cred
def create_user(username=None, password=None):
    j = request.json.get
    print('username: ', username)
    print('password: ', password)
    email = j('email')
    print('email: ', email)
    if not email or email == '':
        return {'error': True, 'emailInvalid': True, 'emailError': 'Empty'}
    if not check_email(email):
        return {'error': True, 'emailInvalid': True, 'emailError': 'Unaccepted'}
    if not username or username == '':
        return {'error': True, 'usernameInvalid': True, 'usernameError': 'Empty'}
    if not password or password == '':
        return {'error': True, 'passwordInvalid': True, 'passwordError': 'Empty'}
    if User.query.filter_by(username=username).first():
        return {
            'error': True,
            'usernameInvalid': True,
            'usernameError': 'Username taken'
        }
    user = User(username, password, email)
    return {'token': user.get_token()}
