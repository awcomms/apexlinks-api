import json
from app import db
from app.api import bp
from app.misc import cdict
from app.user_model import User
from app.item_model import Item
from flask import request
from flask_jwt_extended import jwt_required

@bp.route('/items', methods=['GET'])
def items():
    a = request.args.get
    user = None
    token = request.headers.get('Token')
    if token:
        try:
            user = User.query.filter_by(token=token).first()
        except:
            user = None
    id = a('id')
    if id:
        try:
            id = int(id)
        except:
            return {'error': 'Invalid id type'}, 400
        user = User.query.get(id)
        if not user:
            return '404'
        if not user.visible:
            return '423'
    try:        
        page = int(a('page'))
    except:
        page = 1
    visible = a('visible')
    if visible == 'true':
        visible = True
    elif visible == 'false':
        visible = False
    else:
        visible = True
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    return cdict(Item.fuz(user, id, visible, tags), page)

@bp.route('/items', methods=['POST'])
def add_item():
    token = request.headers.get('Token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401', 401
    json = request.json.get
    name = json('name')
    itype = json('itype')
    price = json('price')
    if Item.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another item owned by same user has that name'}
    tags = json('tags') or []
    if name and name not in tags: tags.append(name)
    data = {
        'name': name,
        'itype': itype,
        'itext': json('itext'),
        'visible': json('visible'),
        'redirect': json('redirect'),
        'images': json('images'),
        'image': json('image'),
        'link': json('link'),
        'price': price,
        'user': user,
        'tags': tags
    }
    i = Item(data)
    return {'id': i.id}

@bp.route('/items', methods=['PUT'])
def edit_item():
    token = request.headers.get('Token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    json = request.json.get
    print(json('link'))
    id = json('id')
    item = Item.query.get(id)
    name = json('name')
    itype = json('itype')
    price = json('price')
    if name != item.name and Item.query\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Author already has item with same name'}, 400
    if item and item.user != user:
        return '', 401
    tags = json('tags') or []
    if name and name not in tags: tags.append(name)
    if itype and itype not in tags: tags.append(itype)
    data = {
        'itext': json('itext'),
        'visible': json('visible'),
        'images': json('images'),
        'image': json('image'),
        'link': json('link'),
        'redirect': json('redirect'),
        'itype': itype,
        'price': price,
        'name': name,
        'tags': tags
    }
    item.edit(data)
    return {'id': item.id}

@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    try:
        id = int(id)
    except:
        return {'error': 'Invalid id type'}, 400
    return Item.query.get(id).dict()

@bp.route('/items/<int:id>', methods=['DELETE'])
def del_item(id):
    token = request.headers.get('Token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    item = Item.query.get(id)
    if item.user != user:
        return '', 401
    db.session.delete(item)
    db.session.commit()
    return {'yes': True}