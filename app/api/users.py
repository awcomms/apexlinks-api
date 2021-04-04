import json
from flask_jwt_extended import jwt_required, create_access_token
from flask import jsonify, request
from app import db
from app.api import bp
from app.user_models import User
from app.misc import cdict

#returns `False` if username exists
@bp.route('/check_username/<username>')
def check_username(username):
    return {'res': User.query.filter_by(username=username).count()<1}

@bp.route('/users', methods=['GET'])
def users():
    a = request.args.get
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1
    return cdict(User.fuz(tags), page)

@bp.route('/users/<value>', methods=['GET'])
def user(value):
    try:
        user = User.query.get(int(value))
    except:
        user = User.query.filter_by(username=value).first()
    if not user:
        return '', 404
    return user.dict()

@bp.route('/users', methods=['POST'])
def create_user():
    j = request.json.get
    username = j('username')
    password = j('password')
    if not username or username == '':
        return {'usernameInvalid': True}
    if not password or password == '':
        return {'passwordInvalid': True}
    if User.query.filter_by(username=username).first():
        return {
            'usernameInvalid': True,
            'usernameError': 'Username taken'
        }
    user = User(username, password)
    user.token = create_access_token(identity=username)
    db.session.commit()
    return jsonify({'user': user.dict()})

@bp.route('/users', methods=['PUT'])
def edit_user():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    request_json = request.json.get
    username = request_json('username')
    if not username or username == '':
        return {'usernameInvalid': True, 'usernameError': 'No username'}, 400
    if username and username != user.username and \
        User.query.filter_by(username=username).first():
        return {'usernameInvalid': True, 'usernameError': 'Username taken'}, 400
    tags = request_json('tags') or []
    # if user.username != request_json('username'):
    #       tags.pop(tags.index(user.username))
    # if tags.index(user.name) and user.name != request_json('name'):
    #       tags.pop(tags.index(user.name))
    # if tags.index(user.email) and user.email != request_json('email'):
    #       tags.pop(tags.index(user.email))
    # if tags.index(user.phone) and user.phone != request_json('phone'):
    #       tags.pop(tags.index(user.phone))
    # if tags.index(user.website) and user.website != request_json('website'):
    #       tags.pop(tags.index(user.website))
    # if tags.index(user.address) and user.address != request_json('address'):
    #       tags.pop(tags.index(user.address))
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
    for field in data:
        value = data[field]
        if value and not value in tags:
            tags.append(value)
    data['about'] = request_json('about')
    data['visible'] = request_json('visible')
    data['images'] = request_json('images')
    data['image'] = request_json('image')
    data['tags'] = tags
    user.edit(data)
    return user.dict()

@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    for item in user.items:
        db.session.delete(item)
    for room in user.rooms:
        db.session.delete(room)
    db.session.delete(user)
    db.session.commit()
    return {'yes': True}, 202