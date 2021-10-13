from flask import request
from app.api import bp
from app.auth import cred
from app.user_model import User
from app.misc.check_email import check_email

@bp.route('/users', methods=['POST'])
@cred
def create_user(username=None, password=None):
    j = request.json.get
    print('username: ', username)
    print('password: ', password)
    email = j('email')
    print('email: ', email)
    if not email or email == '':
        return {'error': True, 'emailError': 'Empty'}
    if not check_email(email):
        return {'error': True, 'emailError': 'Unaccepted'}
    if not username or username == '':
        return {'error': True, 'usernameInvalid': True, 'usernameError': 'Empty'}
    # warn api users that account will be created without password
    # if (not password or password == '') and not allowEmptyPassword:
    #     return {'error': True, 'passwordInvalid': True, 'passwordError': 'Empty'}
    if User.query.filter_by(username=username).first():
        return {
            'error': True,
            'usernameInvalid': True,
            'usernameError': 'Username taken'
        }
    user = User(username, password, email)
    return {
        'user': user.dict(),
        'token': user.get_token()
        }