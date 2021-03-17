import json
from app import db
from app.api import bp
from app.misc import cdict
from app.user_models import User
from app.group_models import Group
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/groups', methods=['GET'])
def groups():
    a = request.args.get
    id = a('id')
    try:
        id = int(id)
    except:
        id = None
    if id:
        user = User.query.get(id)
        if not user:
            id=None
    visible = a('visible')
    if visible == 'true':
        visible = True
    elif visible == 'false':
        visible = False
    else:
        visible = True
    try:
        tags = json.loads(a('tags'))
        page = int(a('page'))
    except:
        tags = []
        page = 1
    return cdict(Group.fuz(id, visible, tags), page)

@bp.route('/groups', methods=['POST'])
def add_group():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    json = request.json.get
    name = json('name')
    if Group.query.filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another group owned by same user has that name'}
    tags = json('tags') or []
    tags.append(name)
    data = {
        'name': name,
        'visible': json('visible'),
        'user': user,
        'tags': tags
    }
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
    if name != group.name and Group.query\
            .filter_by(name=name).first():
        return {'nameError': 'Name taken'}, 301 #wrong error code
    tags = json('tags') or []
    if group and group.user != user:
        return '', 401
    tags.append(name)
    data = {
        'name': name,
        'visible': json('visible'),
        'tags': tags
    }
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