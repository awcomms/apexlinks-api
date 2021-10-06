from app.email import send_reset_password
import json
from flask import request
from app.api import bp
from app.auth import auth
from app.user_model import User

@bp.route('/forgot_password', methods=['PUT'])
def forgot_password():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            'error': True,
            'usernameInvalid': True,
            'usernameError': 'No user with that username'
        }, 401
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
        return {}

@bp.route('/users', methods=['PUT'])
@auth
def edit_user(user=None):
    request_json = request.json.get
    username = request_json('username')
    print('us', username)
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