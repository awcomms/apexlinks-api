from app.api import bp
from app.geo_models import Place
from app.models import User
from app.item_models import Item
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/items/search', methods=['GET'])
def search_items():
    a = request.args.get
    q = a('q') or ''
    page = a('page')
    lat = a('lat')
    lon = a('lon')
    position = (lat, lon)
    state_id = j('state_id')
    return cdict(Item.fuz(q, position, state_id), page)

@bp.route('/items', methods=['POST'])
@jwt_required
def add_item():
    j = request.json.get
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    data = {
        'user': user,
        'name': j('name'),
        'json': j('json'),
        'about': j('about'),
        'price': j('price'),
        'paid_in': j('paid_in')
    }
    i = Item(user, data)
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
    q = request.json.get
    token = request.headers['Authorization']
    id = q('id')
    name = q('name')
    json = q('json')
    return Item.edit(id, token, name, json)

@bp.route('/items', methods=['GET'])
def items():
    q = request.args.get
    id = q('id')
    page = q('page')
    s = Item.query.filter_by(user_id = id)
    return jsonify(Item.cdict(s, page))

@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    return jsonify(Item.query.get(id).dict())

@bp.route('/items', methods=['DELETE'])
def del_items():
    token = request.headers['Authorization']
    ids = request.args.get('ids')
    return Item.delete(ids, token)