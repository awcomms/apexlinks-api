import json
from flask_jwt_extended import jwt_required, create_access_token
from flask import jsonify, request
from fuzzywuzzy import fuzz
from app import db
from app.api import bp
from app.user_models import User
from app.misc import cdict

@bp.route('/get')
def get():
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    q = request.args.get('q')
    if user.chats:
        for link in user.chats:
            link['score'] = fuzz.token_set_ratio(q, link)
        def by_score(e):
            return e['score']
        user.chats.sort(key=by_score).slice(0, 5)
        return {'items': user.chats}
    else:
        return {'items': []}

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
    return cdict(User.fuz(tags), 1, 1)

@bp.route('/users/<value>', methods=['GET'])
def user(value):
    try:
        user = User.query.get(int(value))
    except:
        user = User.query.filter_by(username=value).first()
    if not user:
        return '', 404
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
    data = request.json.get
    username = data('username')
    if username and username != user.username and \
        User.query.filter_by(username=username).first():
        return {'usernameInvalid': True, 'usernameError': 'Username taken'}, 302 #TODO
    tags = data('tags') or []
    j = {
        'username': username,
        'address': data('address'),
        'website': data('website'),
        'phone': data('phone'),
        'email': data('email'),
        'name': data('name'),
    }
    for field in j:
        if field != user.about:
            i = j[field]
        if i and not i in tags:
            tags.append(i)
    j['socket_id'] = data('socket_id')
    j['visible'] = data('visible')
    j['tags'] = tags
    user.edit(j)
    return user.dict()

@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    for room in user.rooms:
        db.session.delete(room)
    db.session.delete(user)
    db.session.commit()
    return {'yes': True}, 202