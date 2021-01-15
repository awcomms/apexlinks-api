import json
from flask_jwt_extended import jwt_required, create_access_token
from flask import jsonify, request
from app import db
from app.api import bp
from app.geo_models import Place
from app.models import User, cdict

@bp.route('/users/toggle_item_save', methods=['PUT'])
@jwt_required
def toggle_item_save():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.toggle_item_save(id)
    return jsonify({'yes': True})

@bp.route('/users/saved_items')
@jwt_required
def saved_items():
    token = request.headers['Authorization']
    id = request.args.get('id')
    page = request.args.get('page')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    return jsonify(cdict(user.saved_items, page))

@bp.route('/users/item_saved')
@jwt_required
def item_saved():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    res = user.item_saved(id)
    return jsonify({'res': res})

@bp.route('/users/save_item', methods=['PUT'])
@jwt_required
def save_item():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.save_item(id)
    return jsonify({'yes': True})

@bp.route('/users/unsave_item', methods=['PUT'])
@jwt_required
def unsave_item():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.unsave_item(id)
    return jsonify({'yes': True})

@bp.route('/users/toggle_usersave', methods=['PUT'])
@jwt_required
def toggle_user_save():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.toggle_user_save(id)
    return jsonify({'yes': True})

@bp.route('/users/saved_users')
@jwt_required
def saved_users():
    token = request.headers['Authorization']
    id = request.args.get('id')
    page = request.args.get('page')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    return jsonify(cdict(user.saved_users, page))

@bp.route('/users/user_saved')
@jwt_required
def user_saved():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    res = user.user_saved(id)
    return jsonify({'res': res})

@bp.route('/users/save', methods=['PUT'])
@jwt_required
def save_user():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.save_user(id)
    return jsonify({'yes': True})

@bp.route('/users/unsave', methods=['PUT'])
@jwt_required
def unsave_user():
    token = request.headers['Authorization']
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    user.unsave_user(id)
    return jsonify({'yes': True})

@bp.route('/del_card', methods=['PUT'])
@jwt_required
def del_card():
    j = request.json.get
    token = request.headers['Authorization']
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
@jwt_required
def user_saved_items():
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    page = request.args.get('page')
    return cdict(user.saved_items, page)

@bp.route('/users')
def users():
    a = request.args.get
    q = a('q') or ''
    sort = a('sort')
    page = a('page')
    tags = json.loads(a('tags'))
    coords = None
    position = None
    if a(position):      
        coords = json.loads(a('position'))
        position = ( coords['lat'], coords['lng'] )
    nation_id = a('nation_id')
    state_id = a('state_id')
    return cdict(User.fuz(q, sort, tags, position, nation_id, state_id), page)

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
    errors = []
    username = j('username')
    email = j('email')
    password = j('password')
    if username is None:
        errors.append({'id': 1, 'kind': 'error', 'title': 'You must provide a username'})
        return jsonify({'errors': errors})
    if email is None:
        errors.append({'id': 2, 'kind': 'error', 'title': 'You must provide an email'})
        return jsonify({'errors': errors})
    if password is None:
        errors.append({'id': 1, 'kind': 'error', 'title': 'You must provide a password'})
        return jsonify({'errors': errors})
    if User.query.filter_by(username=username).first():
        errors.append({'id': 2, 'kind': 'error', 'title': 'Username taken'})
        return jsonify({'errors': errors})
    if User.query.filter_by(email=email).first():
        errors.append({'id': 1, 'kind': 'error', 'title': 'Email taken'})
        return jsonify({'errors': errors})
    user = User(username, email, password)
    user.token = create_access_token(identity=username)
    return jsonify({'user': user.dict()})

@bp.route('/users', methods=['PUT'])
@jwt_required
def edit_user():
    errors = []
    token = request.headers['Authorization']
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