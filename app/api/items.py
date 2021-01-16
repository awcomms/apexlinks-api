import json
from app.api import bp
from app.misc import cdict
from app.models import User
from app.item_models import Item
from flask import request, jsonify
from flask_jwt_extended import jwt_required

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
    errors = []
    a = request.args.get
    q = a('q') or ''
    id = a('id')
    sort = a('sort')
    page = a('page')
    itype = a('itype')
    tags = None
    _tags = a('tags')
    try:
        if _tags and type(json.loads(_tags)) is list:
                tags = json.loads(_tags)
    except:
        pass
    position = None
    if a('position'):      
        coords = json.loads(a('position'))
        position = ( coords['lat'], coords['lng'] )
    nation_id = a('nation_id')
    state_id = a('state_id')
    return cdict(Item.fuz(q, id, sort, itype, tags, position, nation_id, state_id), page)

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
    print(i)
    return jsonify({'id': i.id})

@bp.route('/items', methods=['PUT'])
def edit_item():
    errors = []
    j = request.json.get
    token = request.headers.get('Authorization')
    id = a('id')
    item = Item.query.get(id)
    user = User.query.filter_by(token==token).first()
    if item.user != user:
        return {}, 401
    if not item:
        return jsonify({'error': 'item does not exist'})
    if j('name') == '':
        errors.append({'id': 1, 'kind': 'error', 'title': "The name shouldn't be empty"})
        return jsonify({'errors': errors})
    if not j('name'):
        errors.append({'id': 1, 'kind': error, 'title': 'A name is required'})
        return jsonify({'errors': errors})
    if Item.query.filter_by(user_id=user.id).filter_by(name=j('name')):
        errors.append({'id': 1, 'kind': error, 'title': 'One of your items already has that name'})
        return jsonify({'errors': errors})
    data = {
        'name': j('name'),
        'description': j('description'),
        'price': j('price'),
        'paid_in': j('paid_in')
    }
    item.edit(data)
    return jsonify({'id': item.id})

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
    return jsonify(Item.query.get(id).dict())

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