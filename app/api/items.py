import json
from app import db
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
    a = request.args.get
    id = a('id')
    if id:
        user = User.query.get(id)
        if not user:
            return '404'
        if not user.visible:
            return '423'
    page = a('page')
    itype = a('itype')
    visible = a('visible')
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    return cdict(Item.fuz(id, visible, itype, tags), page)

@bp.route('/items', methods=['POST'])
def add_item():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401'
    json = request.json.get
    tags = json('tags')
    name = json('name')
    itype = json('itype')
    data = {
        'description': json('description'),
        'name': name,
    }
    if tags:
        for field in data:
            i = data[field]
            if not i in tags:
                tags.append(i)
    data['visible'] = json('visible')
    data['images'] = json('images')
    data['itype'] = json('itype')
    data['image'] = json('image')
    data['user'] = user
    data['tags'] = tags
    if Item.query.filter_by(itype=itype).filter_by(user_id=user.id).filter_by(name=name).first():
        return {'nameError': 'Another item owned by user has that name'}
    i = Item(data)
    return {'id': i.id}

@bp.route('/items', methods=['PUT'])
def edit_item():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    json = request.json.get
    tags = json('tags')
    name = json('name')
    id = json('id')
    item = Item.query.get(id)
    if item and item.user != user:
        return '401'
    data = {
        'name': name,
        'description': json('description'),
    }
    if tags:
        for data in json:
            i = json[data]
            if not i in tags:
                tags.append(i)
    data['visible'] = json('visible')
    data['images'] = json('images')
    data['itype'] = json('itype')
    data['image'] = json('image')
    data['tags'] = tags
    item.edit(data)
    return {'id': item.id}

@bp.route('/items/toggle_visible/<int:id>', methods=['PUT'])
def toggle_visible(id):
    token = request.headers.get('Authorization')
    if token: user = User.query.filter_by(token=token).first()
    if type(id) == int: item = Item.query.get(id)
    if not item:
        return {'error': 'item does not exist'}
    if not user or item.user != user:
        return {}, 401
    item.visible = not item.visible
    return {'visible': item.visible}

@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    item = Item.query.get(id).dict()
    print(type(item))
    return item

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