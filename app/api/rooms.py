import json
from copy import copy
from flask import request, jsonify
from app import db
from app.api import bp
from app.misc import cdict
from app.user_models import User, xrooms
from app.room_models import Room

@bp.route('/in_room/<int:id>', methods=['PUT'])
def in_room(id):
    token=request.headers.get('Authorization')
    user=User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    room=Room.query.get(id)
    if not room:
        return '', 404
    in_rooms=user.in_rooms
    if id not in in_rooms:
        in_rooms.append(id)
    user.in_rooms=in_rooms
    db.session.commit()
    return user.dict()

@bp.route('/left/<int:id>', methods=['PUT'])
def left(id):
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    room = Room.query.get(id)
    if not room:
        return '', 404
    in_rooms = user.in_rooms
    if id in in_rooms:
        in_rooms.pop(in_rooms.index(id))
    user.in_rooms = in_rooms
    db.session.commit()
    return user.dict()

@bp.route('/join', methods=['PUT'])
def join():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    data = request.json.get
    id = data('id')
    try:
        room = Room.query.get(id)
    except:
        room = None
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
    args = request.args.get
    if not user:
        return '', 401
    try:
        tags = json.loads(args('tags'))
        page = int(args('page'))
    except:
        tags = []
        page = 1
    return cdict(Room.xfuz(user.id, tags), page, 100, 'rooms')

@bp.route('/rooms', methods=['GET'])
def rooms():
    print(request.origin)
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
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
    try:
        tags = json.loads(a('tags'))
        page = int(a('page'))
    except:
        tags = []
        page = 1
    query = Room.fuz(id, tags)
    for room in query:
        if room.id in user.unseen_rooms:
            room.unseen = True
        else:
            room.unseen = False
    db.session.commit()
    return cdict(query, page)

@bp.route('/rooms', methods=['POST'])
def add_room():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    data = request.json.get
    open = data('open')
    username = data('username')
    name = data('name')
    if Room.query.filter_by(name=name).first():
        return {'nameError': 'name taken'}, 423
    tags = data('tags') or []
    tags.append(name)
    data = {
        'name': name,
        'user': user,
        'open': open,
        'tags': tags
    }
    room = Room(data)
    user.join(room)
    if username and not open:
        user2 = User.query.filter_by(username=username).first()
        if user2:
            user2.join(room)
    return {'id': room.id}

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

@bp.route('/rooms/<value>', methods=['GET'])
def get_room(value):
    print(request.origin)
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    try:
        room = Room.query.get(int(value))
    except:
        room = Room.query.filter_by(name=value).first()
    if not room:
        return '', 404
    return room.dict()

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