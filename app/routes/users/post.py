from flask import request
from app.auth import cred
from app.routes import bp
from app.models.user import User
from app.misc.check_include import check_include

@bp.route('/users', methods=['POST'])
@cred
def create_user(username=None, password=None):
    try:
        include = check_include(request.args.get('include'))
    except Exception as e:
        return e.args[0]
    j = request.json.get
    email = j('email')
    location = j('location')
    # email is optional
    # if not email or email == '':
    #     return {'error': True, 'emailError': 'Empty'}
    # if not check_email(email):
    #     return {'error': True, 'emailError': 'Unaccepted'}
    if not username or username == '':
        return {'error': True, 'usernameInvalid': True, 'usernameError': 'Empty'}
    # warn api users that account will be created without password
    # if (not password or password == '') and not allowEmptyPassword:
    #     return {'error': True, 'passwordInvalid': True, 'passwordError': 'Empty'}
    if User.query.filter_by(username=username).first():
        return {
            'error': 'Username taken',
            'usernameInvalid': True,
            'usernameError': 'Username taken'
        }, 400
    user = User(username, password, email)
    # user.location = location
    # db.session.commit()
    return {
        'user': user.dict(include),
        'token': user.get_token()
    }, 201
