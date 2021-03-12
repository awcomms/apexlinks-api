import json
from app import db
from app.api import bp
from app.misc import cdict
from app.models import User
from app.group_models import Group
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/groups', methods=['GET'])
def groups():
    a = request.args.get
    id = a('id')
    if id:
        user = User.query.get(id)
        if not user:
            return '404'
        if not user.visible:
            return '423'
    page = int(a('page'))
    itype = a('itype')
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
    return cdict(Group.fuz(id, visible, itype, tags), page)

@bp.route('/groups', methods=['POST'])
def add_group():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401', 401
    json = request.json.get
    name = json('name')
    itype = json('itype')
    price = json('price')
    if Group.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another group owned by same user has that name'}
    tags = json('tags') or []
    tags.append(name)
    tags.append(price)
    data = {
        'name': name,
        'itype': itype,
        'description': json('description'),
        'visible': json('visible'),
        'images': json('images'),
        'image': json('image'),
        'price': price,
        'user': user,
        'tags': tags
    }
    # if tags:
    #     for field in data:
    #         i = data[field]
    #         if not i in tags:
    #             tags.append(i)
    i = Group(data)
    return {'id': i.id}

@bp.route('/groups', methods=['PUT'])
def edit_group():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    json = request.json.get
    id = json('id')
    group = Group.query.get(id)
    name = json('name')
    itype = json('itype')
    price = json('price')
    if name != group.name and Group.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another group owned by same user has that name'}, 301 #wrong error code
    tags = json('tags') or []
    if group and group.user != user:
        return '', 401
    tags.append(name)
    tags.append(price)
    data = {
        'name': name,
        'description': json('description'),
        'visible': json('visible'),
        'images': json('images'),
        'itype': json('itype'),
        'image': json('image'),
        'price': price,
        'tags': tags
    }
    # if tags:
    #     for field in data:
    #         i = data[field]
    #         if not i in tags:
    #             tags.append(i)
    group.edit(data)
    return {'id': group.id}

@bp.route('/groups/<int:id>', methods=['GET'])
def group(id):
    return Group.query.get(id).dict()

@bp.route('/groups/<int:id>', methods=['DELETE'])
def del_group(id):
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    group = Group.query.get(id)
    if group.user != user:
        return '', 401
    db.session.delete(group)
    db.session.commit()
    return jsonify({'yes': True})