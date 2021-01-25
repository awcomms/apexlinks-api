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

@bp.route('/check_email/<email>')
def check_email(email):
    return {'res': User.query.filter_by(email=email).count()<1}

@bp.route('/users/saved_items')
def saved_items():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    page = request.args.get('page')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    return jsonify(cdict(user.saved_items, page))

@bp.route('/users/item_saved')
def item_saved():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    res = user.item_saved(id)
    return jsonify({'res': res})

@bp.route('/users/toggle_save', methods=['PUT'])

def toggle_user_save():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    _user = User.query.get(id)
    saved = user.toggle_save(_user)
    return jsonify({'saved': saved})

@bp.route('/users/saved_users')

def saved_users():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    page = request.args.get('page')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    return jsonify(cdict(user.saved_users, page))

@bp.route('/users/user_saved')

def user_saved():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    res = user.user_saved(id)
    return jsonify({'res': res})

@bp.route('/del_card', methods=['PUT'])

def del_card():
    j = request.json.get
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    card = Card.query.get(j('id'))
    if not card:
        return jsonify({'error': 'card does not exist'})
    db.session.delete(card)
    db.session.commit()
    return {}, 202

@bp.route('/user/saved', methods=['GET'])

def user_saved_items():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    page = request.args.get('page')
    return cdict(user.saved_items, page)

@bp.route('/users')
def users():
    a = request.args.get
    q = a('q') or ''
    sort = a('sort')
    page = a('page')
    try:
        tags = json.loads(a('tags'))
    except: tags = []
    try:   
        coords = json.loads(a('location'))
        location = ( coords['lat'], coords['lon'] )
    except: location = None
    nation_id = a('nation_id')
    state_id = a('state_id')
    return cdict(User.fuz(q, sort, tags, location, nation_id, state_id), page)

@bp.route('/user')
def user():
    errors = []
    id = request.args.get('id')
    email = request.args.get('email')
    if id:
        user = User.query.get(id)
    if email:
        user = User.query.filter_by(email=email).first()
    if not user.subscribed:
        errors.append('not_subscribed')
        return jsonify({'errors': errors})
    if not user.visible:
        errors.append('not_visible')
        return jsonify({'errors': errors})
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
        return {'usernameInvalid': True}
    user = User(username, password)
    user.token = create_access_token(identity=username)
    return jsonify({'user': user.dict()})

@bp.route('/users', methods=['PUT'])
def edit_user():
    errors = []
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    data = request.get_json()
    if not user:
        return {}, 401
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        errors.append({'id': 1, 'kind': 'error', 'title': 'Username taken'})
        return jsonify({'errors': errors})
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        errors.append({'id': 2, 'kind': 'error', 'title': 'Email taken'})
        return jsonify({'errors': errors})
    user.edit(data)
    db.session.commit()
    return jsonify({'user': user.dict()})