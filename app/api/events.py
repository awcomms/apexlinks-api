import json
from app import db
from app.api import bp
from app.misc import cdict
from app.models import User
from app.event_models import Event
from flask import request, jsonify
from flask_jwt_extended import jwt_required

@bp.route('/events/toggle_save', methods=['PUT'])
def toggle_event_save():
    token = request.headers.get('Authorization')
    id = request.args.get('id')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    event = Event.query.get(id)
    saved = event.toggle_save(user)
    return jsonify({'saved': saved})

@bp.route('/events', methods=['GET'])
def events():
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
    return cdict(Event.fuz(id, visible, itype, tags), page)

@bp.route('/events', methods=['POST'])
def add_event():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401', 401
    json = request.json.get
    name = json('name')
    itype = json('itype')
    price = json('price')
    if Event.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another event owned by same user has that name'}
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
    i = Event(data)
    return {'id': i.id}

@bp.route('/events', methods=['PUT'])
def edit_event():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    json = request.json.get
    id = json('id')
    event = Event.query.get(id)
    name = json('name')
    itype = json('itype')
    price = json('price')
    if name != event.name and Event.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another event owned by same user has that name'}, 301 #wrong error code
    tags = json('tags') or []
    if event and event.user != user:
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
    event.edit(data)
    return {'id': event.id}

@bp.route('/events/<int:id>', methods=['GET'])
def event(id):
    return Event.query.get(id).dict()

@bp.route('/events/<int:id>', methods=['DELETE'])
def del_event(id):
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '', 401
    event = Event.query.get(id)
    if event.user != user:
        return '', 401
    db.session.delete(event)
    db.session.commit()
    return jsonify({'yes': True})