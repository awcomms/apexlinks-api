import json
from app.api import bp
from app.geo_models import Place
from app.models import cdict, User
from app.item_models import Item
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/items', methods=['GET'])
def items():
    a = request.args.get
    q = a('q') or ''
    id = (a('id'))
    page = a('page')
    itype = a('itype')
    tags = json.loads(a('tags'))
    coords = None
    position = None
    if a(position):      
        coords = json.loads(a('position'))
        position = ( coords['lat'], coords['lng'] )
    nation_id = a('nation_id')
    state_id = a('state_id')
    return cdict(Item.fuz(id, itype, tags, q, position, nation_id, state_id), page)

@bp.route('/items', methods=['POST'])
@jwt_required
def add_item():
    j = request.json.get
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    print(user)
    if not user:
        return {}, 401
    data = {
        'user': user,
        'name': j('name'),
        'json': j('json'),
        'description': j('description'),
        'price': j('price'),
        'paid_in': j('paid_in')
    }
    i = Item(data)
    return jsonify(i.dict())

@bp.route('/item/viewed/<int:id>', methods=['PUT'])
def viewed(id):
    json = request.json.get
    if request.headers.get('Origin') != app.config['FRONT_END']:
        return abort(401)
    ip = json('ip')
    item = Item.query.get(id)
    item.json

@bp.route('/items/save', methods=['PUT'])
@jwt_required
def save_item(id):
    token = request.headers['Authorization']
    ids = request.json.get('ids')
    return Item.save(ids, token)

@bp.route('/item/unsave', methods=['PUT'])
@jwt_required
def unsave_item(id):
    token = request.headers['Authorization']
    ids = request.json.get('ids')
    return Item.unsave(ids, token)

@bp.route('/items/archive/<int:id>', methods=['PUT'])
@jwt_required
def archive_item(id):
    token = request.headers['Authorization']
    return Item.archive(id, token)

@bp.route('/items/unarchive/<int:id>', methods=['PUT'])
@jwt_required
def unarchive_item(id):
    token = request.headers['Authorization']
    return Item.unarchive(id, token)

@bp.route('/items', methods=['PUT'])
@jwt_required
def edit_item():
    a = request.args.get
    token = request.headers['Authorization']
    id = a('id')
    item = Item.query.get(id)
    user = User.query.filter(User.token=token).first()
    if item.user != user:
        return {}, 401
    if not item:
        return jsonify({'error': 'item does not exist'})
    item.edit(data)
    return jsonify({'yes': True})

@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    return jsonify(Item.query.get(id).dict())

@bp.route('/items', methods=['DELETE'])
def del_items():
    token = request.headers['Authorization']
    ids = request.args.get('ids')
    return Item.delete(ids, token)