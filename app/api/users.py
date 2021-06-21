from app.email import send_reset_password
import json
from flask import request
from app import db
from app.api import bp
from app.auth import auth
from app.auth import cred
from app.user_model import User
from app.misc import cdict
from app.misc import check_email

@bp.route('/forgot_password', methods=['PUT'])
def forgot_password():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'usernameInvalid': True, 'usernameError': 'No user with that username'}, 401
    if user.email:
        send_reset_password(user)
    else:
        return {'r': 'No email set for this user'}, 404
    return {'r': 'Check for an email'}

@bp.route('/reset_password', methods=['PUT'])
def reset_password():
    token = request.headers.get('token')
    password = request.json.get('password')
    user = User.check_reset_password_token(token)
    if user:
        user.set_password(password)
        return {'r': True}
    else:
        return ''

@bp.route('/check_reset_password_token', methods=['GET'])
def check_reset_password_token():
    token = request.headers.get('token')
    if User.check_reset_password_token(token):
        return {'r': True}
    else:
        return ''

#returns `False` if username exists
@bp.route('/check_username/<username>', methods=['GET'])
def check_username(username):
    return {'res': User.query.filter_by(username=username).count()<1}

@bp.route('/users', methods=['GET'])
def users():
    a = request.args.get
    id = a('id')
    user = None
    try:
        id = int(id)
    except:
        id = None
    if id:
        user = User.query.get(id)
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1
    return cdict(User.fuz(user, tags), page)

@bp.route('/users', methods=['POST'])
@cred
def create_user(username=None, password=None):
    j = request.json.get
    username = j('username')
    password = j('password')
    email = j('email')
    if not email or email == '':
        return {'emailInvalid': True, 'emailError': 'Empty'}
    if not check_email(email):
        return {'emailInvalid': True, 'emailError': 'Unaccepted'}
    if not username or username == '':
        return {'usernameInvalid': True, 'usernameError': 'Empty'}
    if not password or password == '':
        return {'passwordInvalid': True, 'passwordError': 'Empty'}
    if User.query.filter_by(username=username).first():
        return {
            'usernameInvalid': True,
            'usernameError': 'Username taken'
        }
    user = User(username, password, email)
    user.token = ''
    db.session.commit()
    return {'token': user.token}

@bp.route('/users', methods=['PUT'])
@auth
def edit_user(user=None):
    request_json = request.json.get
    username = request_json('username')
    if not username or username == '':
        return {'usernameInvalid': True, 'usernameError': 'No username'}, 400
    if username and username != user.username and \
        User.query.filter_by(username=username).first():
        return {'usernameInvalid': True, 'usernameError': 'Username taken'}, 400
    tags = request_json('tags') or []
    if type(tags) != list:
        try:
            tags = json.loads(tags)
        except SyntaxError or TypeError:
            tags = tags.split(',')
        except SyntaxError or TypeError:
            tags = tags.split(';')
        except SyntaxError or TypeError:
            return 'Unsupported tags format', 415
    data = {
        'username': username,
        'address': request_json('address'),
        'website': request_json('website'),
        'phone': request_json('phone'),
        'email': request_json('email'),
        'name': request_json('name'),
    }
    # for field in data:
    #     for tag in tags:
    #         #use regex to check for colon definition #TODO
    #         pass
    #     value = data[field]
    #     if value:
    #         # tag = f'{field}: {value}'
    #         tags.append(value)
    # tags.append(username)
    # tags.append(data['name'])
    data['show_email'] = request_json('show_email')
    data['about'] = request_json('about')
    data['hidden'] = request_json('hidden')
    data['images'] = request_json('images')
    data['image'] = request_json('image')
    data['tags'] = tags
    user.edit(data)
    return user.dict()

@bp.route('/users/<int:id>', methods=['DELETE'])
@auth
def delete_user(id, user=None):
    for item in user.items:
        db.session.delete(item)
    db.session.delete(user)
    db.session.commit()
    return {'yes': True}, 202