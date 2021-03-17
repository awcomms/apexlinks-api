import json
from app import db
from app.api import bp
from app.misc import cdict
from app.user_models import User
from app.room_models import Room
from flask import request, jsonify

@bp.route('/join', methods=['PUT'])
def join():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    data = request.json.get
    id = data('id')
    room = Room.query.get(id)
    if not room:
        name = data('name')
        room = Room({'private': True, 'name': name})
    user.join(room)
    return '', 202

@bp.route('/leave', methods=['PUT'])
def leave():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    id = request.json.get('id')
    room = Room.query.get(id)
    if not room:
        return '', 404
    user.leave(room)
    return '', 202

@bp.route('/xrooms', methods=['GET'])
def xrooms():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    try:
        tags = json.loads(a('tags'))
        page = int(a('page'))
    except:
        tags = []
        page = 1
    return cdict(Room.fuz(user.id, tags), page, 100, 'rooms')

@bp.route('/rooms', methods=['GET'])
def rooms():
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
    return cdict(Room.fuz(id, visible, tags), page)

@bp.route('/rooms', methods=['POST'])
def add_room():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    open = data('open')
    data = request.data.get
    name = data('name')
    if Room.query.filter_by(name=name).first():
        return {'nameError': 'name taken'}, 423
    tags = data('tags') or []
    tags.append(name)
    data = {
        'name': name,
        'visible': data('visible'),
        'user': user,
        'open': open,
        'tags': tags
    }
    i = Room(data)
    return {'id': i.id}

@bp.route('/rooms', methods=['PUT'])
def edit_room():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    data = request.data.get
    id = data('id')
    room = Room.query.get(id)
    name = data('name')
    open = data('open')
    if name != room.name and Room.query\
            .filter_by(name=name).first():
        return {'nameError': 'Name taken'}, 301 #wrong error code
    tags = data('tags') or []
    if room and room.user != user:
        return '', 401
    tags.append(name)
    data = {
        'name': name,
        'open': open,
        'tags': tags
    }
    room.edit(data)
    return {'id': room.id}

@bp.route('/rooms/<int:id>', methods=['GET'])
def room(id):
    return Room.query.get(id).dict()

@bp.route('/rooms/<int:id>', methods=['DELETE'])
def del_room(id):
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    room = Room.query.get(id)
    if room.user != user:
        return '', 401
    db.session.delete(room)
    db.session.commit()
    return jsonify({'yes': True})