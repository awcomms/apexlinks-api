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

@bp.route('/join/<int:id>', methods=['PUT'])
@auth
def join(id, user=None):
    room = Room.query.get(id)
    if not room:
        return {"error": f"room {id} not found"}, 404
    user.join(room)
    return {}, 202

@bp.route('/leave', methods=['PUT'])
@auth
def leave(user=None):
    id = request.json.get('room')
    room = Room.query.get(id)
    if not room:
        return {"error": f"room {id} not found"}, 404
    user.leave(room)
    return {}, 202

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

    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1

    run = Room.get(tags, limit)
    return cdict(query, page, run=run, user=user)

@bp.route('/rooms', methods=['POST'])
@auth
def add_room(user=None):
    data = request.json.get
    # open = data('open')
    name = data('name')
    if Room.query.filter_by(name=name).first():
        return {'nameError': 'Name taken'}, 423
    tags = data('tags') or []
    if not name in [t['value'] for t in tags]:
        tags.append({'value': name})
    data = {
        'name': name,
        'user': user,
        # 'open': open,
        'tags': tags,
        # 'about': data['about']
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
    if not room:
        return {"error": f"room {id} not found"}
    name = data('name')
    if name != room.name and Room.query\
            .filter_by(name=name).first():
        return {'nameError': 'Name taken by a different room'}, 400 #wrong error code
    tags = data('tags') or []
    if room and room.user != user:
        return {"error": "authenticated user did not create this room"}, 401
    if not name in [t['value'] for t in tags]:
        tags.append({'value': name})
    data = {
        'name': name,
        'tags': tags,
        'about': data('about')
    }

    room.edit(data)

    return {'id': room.id}

@bp.route('/rooms/<value>', methods=['GET'])
def get_room(value, user=None):
    try:
        room = Room.query.get(int(value))
    except:
        room = Room.query.filter_by(name=value).first()
    if not room:
        return '', 404
    if user:
        db.engine.execute(xrooms.update().where(xrooms.c.user_id==user.id)\
            .where(xrooms.c.room_id==room.id).values(seen=True))
    return room.dict()

@bp.route('/rooms/<int:id>', methods=['DELETE'])
def del_room(id, user=None):
    room = Room.query.get(id)
    if room.user != user:
        return '', 401
    db.session.delete(room)
    db.session.commit()
    return jsonify({'yes': True})