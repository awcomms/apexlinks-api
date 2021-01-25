import json
from app.api import bp
from app.misc import cdict
from app.models import User
from app.item_models import Item
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/name_available', methods=['GET'])
def name_available():
    a = request.args.get
    id = a('id')
    name=a('name')
    item = Item.query.get(id)
    user = User.query.filter_by(token=token).first()
    if not item:
        return {'error': 'item does not exist'}
    if not name or name == '':
        return {'error': 'no name'}
    if Item.query.filter(Item.id != id).filter_by(user_id=user.id).filter_by(name=name):
        return {'error': 'Another item of yours has that name'}

@bp.route('/items/toggle_save', methods=['PUT'])
def toggle_item_save():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    item = Item.query.get(id)
    saved = item.toggle_save(user)
    return jsonify({'saved': saved})

@bp.route('/items', methods=['GET'])
def items():
    a = request.args.get
    q = a('q') or ''
    id = a('id')
    sort = a('sort')
    page = a('page')
    itype = a('itype')
    archived = a('archived')
    try:
        tags = json.loads(a('tags'))
    except:
        tags = None
    nation_id = a('nation_id')
    state_id = a('state_id')
    return cdict(Item.fuz(id, archived, itype, tags), page)

@bp.route('/items', methods=['POST'])
def add_item():
    errors = []
    data = request.get_json()
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    itype = data['itype']
    name = data['name']
    data['user'] = user
    if not name:
        errors.append({'id': 1, 'kind': 'error', 'title': 'A name is required'})
        return jsonify({'errors': errors})
    if Item.query.filter_by(itype=itype).filter_by(user_id=user.id).filter_by(name=name).first():
        errors.append({'id': 1, 'kind': 'error', 'title': f'One of your {itype}s already has that name'})
        return jsonify({'errors': errors})
    i = Item(data)
    return {'res': True}

@bp.route('/items', methods=['PUT'])
def edit_item():
    errors = []
    j = request.json.get
    print(request.get_json())
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    id = j('id')
    name = j('name')
    item = Item.query.get(id)
    if item and item.user != user:
        return {}, 401
    data = {
        'name': name,
        'itype': j('itype'),
        'price': j('price'),
        'archived': j('archived')}
    item.edit(data)
    print(item.dict())
    return {'yes': True}

@bp.route('/items/toggle_archive/<int:id>', methods=['PUT'])
def toggle_archive(id):
    token = request.headers.get('Authorization')
    if token: user = User.query.filter_by(token=token).first()
    if type(id) == int: item = Item.query.get(id)
    if not item:
        return {'error': 'item does not exist'}
    if not user or item.user != user:
        return {}, 401
    item.archived = not item.archived
    return {'archived': item.archived}

@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    return Item.query.get(id).dict()

@bp.route('/items/<int:id>', methods=['DELETE'])
def del_item(id):
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    item = Item.query.get(id)
    if item.user != user:
        return {}, 401
    db.session.delete(item)
    return jsonify({'yes': True})