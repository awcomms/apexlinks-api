import json
from flask_jwt_extended import jwt_required, create_access_token
from flask import jsonify, request
from app import db
from app.api import bp
from app.models import User
from app.misc import cdict

#returns `False` if username exists
@bp.route('/check_username/<username>')
def check_username(username):
    return {'res': User.query.filter_by(username=username).count()<1}

@bp.route('/users', methods=['GET'])
def users():
    # a = request.args.get
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401', 401
    tags = user.tags
    # page = int(a('page'))
    return cdict(User.fuz(tags), 1, 1)

@bp.route('/user/<value>', methods=['GET'])
def user(value):
    try:
        user = User.query.get(int(value))
    except:
        user = User.query.filter_by(username=value).first()
    if not user:
        return '404', 404
    return jsonify(user.dict())

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
    return jsonify({'user': user.dict()})

@bp.route('/users', methods=['PUT'])
def edit_user():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    _json = request.json.get
    username = _json('username')
    if not username or username == '':
        return {'usernameInvalid': True, 'usernameError': 'No username'}
    if username and username != user.username and \
        User.query.filter_by(username=username).first():
        return {'usernameInvalid': True, 'usernameError': 'Username taken'}
    tags = _json('tags') or []
    # if type(tags) != list:
    #     try:
    #         tags = json.loads(tags)
    #     except:
    #         tags = tags.split(',')
    #     except:
    #         tags = tags.split(';')
    #     finally:
    #         return 'Unsupported tags format', 301
    j = {
        'username': username,
        'address': _json('address'),
        'website': _json('website'),
        'phone': _json('phone'),
        'email': _json('email'),
        'name': _json('name'),
    }
    for data in j:
        if data != user.about:
            i = j[data]
        if not i in tags:
            if i:
                tags.append(i)
    j['visible'] = _json('visible')
    j['code'] = _json('code')
    j['tags'] = tags
    user.edit(j)
    return user.dict()

@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    for group in user.groups:
        db.session.delete(group)
    db.session.delete(user)
    db.session.commit()
    return {'yes': True}, 202