import json
from flask import request, jsonify
from app import db
from app.auth import auth
from app.routes import bp
from app.vars.q import room_search_fields
from app.misc.sort.tag_sort import tag_sort
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
    query = Room.query
    args = request.args.get

    id = args('id')
    if id:
        try:
            id = int(id)
        except:
            return {'error': f'id should have a type of number'}
        user = User.query.get(id)
        if not user:
            return {'error': f'user with id {id} was not found'}
        
        query = query.join(xrooms).filter(xrooms.c.user_id == id)
    
    try:
        tags = json.loads(args('tags'))
    except:
        tags = []

    try:
        page = int(args('page'))
    except:
        page = 1

    run = Room.get(tags)
    return cdict(query, page, run=run)

@bp.route('/rooms', methods=['GET'])
@auth
def rooms(user=None):
    query = Room.query.join(User)
    a = request.args.get
    id = a('id')
    if id:
        try:
            id = int(id)
        except:
            return {'error': f'id should have a type of number'}
        user = User.query.get(id)
        if not user:
            return {'error': f'user with id {id} was not found'}
        query = query.filter(User.id == id)

    limit = a('limit')
    if limit:
        try:
            limit = int(limit)
        except:
            return {'error': "'limit' query arg should be a number"}
    else:
        limit = 0

    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1

    run = Room.get(tags, limit)
    return cdict(query, page, run=run)

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