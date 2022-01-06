import json
from flask import request, jsonify
from app import db
from app.auth import auth
from app.routes import bp
from app.misc.cdict import cdict
from app.models.user import User, xrooms
from app.models.room import Room

@bp.route('/seen', methods=['PUT'])
@auth
def seen(user=None):
    id = request.args.get('id')
    room = Room.query.get(id)
    if not room:
        return '404', 404
    db.engine.execute(xrooms.update().where(xrooms.c.user_id==user.id)\
        .where(xrooms.c.room_id==room.id).values(seen=True))
    return '202', 202

@bp.route('/join', methods=['PUT'])
@auth
def join(user=None):
    data = request.json.get
    id = data('id')
    try:
        room = Room.query.get(id)
    except:
        room = None
    user.join(room)
    return '', 202

@bp.route('/leave', methods=['PUT'])
@auth
def leave(user=None):
    token = request.headers.get('auth')
    id = request.json.get('id')
    room = Room.query.get(id)
    if not room:
        return '', 404
    user.leave(room)
    if not room.open:
        db.session.delete(room)
        db.session.commit()
    return '', 202

@bp.route('/xrooms', methods=['GET'])
@auth
def get_xrooms(user=None):
    args = request.args.get
    try:
        tags = json.loads(args('tags'))
        page = int(args('page'))
    except:
        tags = []
        page = 1
    query = Room.xfuz(user.id, tags)
    return cdict(query, page, 100, user=user)

@bp.route('/rooms', methods=['GET'])
@auth
def rooms(user=None):
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
    return cdict(query, page, user=user)

@bp.route('/rooms', methods=['POST'])
@auth
def add_room(user=None):
    data = request.json.get
    # open = data('open')
    name = data('name')
    if Room.query.filter_by(name=name).first():
        return {'nameError': 'Name taken'}, 423
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
    return {'id': room.id}

@bp.route('/rooms', methods=['PUT'])
@auth
def edit_room(user=None):
    data = request.json.get
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
@auth
def get_room(value, user=None):
    try:
        room = Room.query.get(int(value))
    except:
        room = Room.query.filter_by(name=value).first()
    if not room:
        return '', 404
    db.engine.execute(xrooms.update().where(xrooms.c.user_id==user.id)\
        .where(xrooms.c.room_id==room.id).values(seen=True))
    return room.dict(user=user)

@bp.route('/rooms/<int:id>', methods=['DELETE'])
def del_room(id, user=None):
    room = Room.query.get(id)
    if room.user != user:
        return '', 401
    db.session.delete(room)
    db.session.commit()
    return jsonify({'yes': True})