from flask_jwt_extended import jwt_required, create_access_token
from flask import g, abort, jsonify, request, url_for
from app import db
from app.api import bp
from app.geo_models import Place
from app.models import User, cdict
from app.email import send_user_email
#from app.api.auth import token_auth
from app.api.errors import res, bad_request

@bp.route('/users/from_place', methods=['GET'])
def get_users_from_place():
    a = request.args.get
    id = a('id')
    page = a('page')
    query = User.query.filter_by(place_id=id)
    return cdict(query, page)

@bp.route('/user/saved', methods=['GET'])
@jwt_required
def user_saved_items():
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    page = request.args.get('page')
    return cdict(user.saved_items, page)

@bp.route('/users/search', methods=['PUT'])
def search_users():
    j = request.json.get
    q = j('q') or ''
    page = j('page')
    position = j('position')
    return User.search(q, page, position)

@bp.route('/user/<int:id>', methods=['GET'])
def user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.qdict())

@bp.route('/users/items', methods=['GET'])
def items():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Item.query.filter_by(user_id = id)
    return jsonify(Item.cdict(s, page))

@bp.route('/users', methods=['GET'])
@jwt_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    user = User.to_cdict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    q = request.get_json()
    errors = []
    email = q['email']
    password = q['password']
    if email is None:
        errors.append({'id': 1, 'kind': 'error', 'title': 'You must provide an email'})
        return jsonify({'errors': errors})
    if password is None:
        errors.append({'id': 1, 'kind': 'error', 'title': 'You must provide a password'})
        return jsonify({'errors': errors})
    if User.query.filter_by(email=email).first():
        errors.append({'id': 1, 'kind': 'error', 'title': 'email taken'})
        return jsonify({'errors': errors})
    user = User(email, password)
    user.token = create_access_token(identity=email)
    pring(user.token)
    res = jsonify({'user': user.dict()})
    res.status_code = 201
    return res

@bp.route('/user/<int:id>', methods=['PUT'])
@jwt_required
def edit_user(id):
    errors = []
    print(request.get_json())
    token = request.headers['Authorization']
    user = User.query.get_or_404(id)
    data = request.get_json()
    if user != User.query.filter_by(token = token).first():
        return {}, 401
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        errors.append('email taken')
        return {'errors': errors}
    user.from_dict(data)
    for item in user.items:
        item.location = user.location
    db.session.commit()
    return {'user': user.dict()}