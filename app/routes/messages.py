from flask import request
from app.routes import bp
from app import db
from app.misc import cdict
from app.models.user import User, xrooms
from app.models.room import Room
from app.models.message import Message

@bp.route('/messages')
def get_messages():
    args = request.args.get
    id = args('id')
    page = args('page')
    try:
        room = Room.query.get(id)
    except:
        return '', 404
    try:
        page = int(page)
    except:
        page = 1
    messages = room.messages.order_by(Message.timestamp.asc())
    return cdict(messages, page, 100)

@bp.route('/messages', methods=['PUT'])
def post_message():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user: 
        return '', 401
    data = request.json.get
    id = data('id')
    room = Room.query.get(id)
    if not room:
        return '', 404
    value = data('value')
    Message(value, user, room)
    db.engine.execute(xrooms.update().where(xrooms.c.room_id==room.id).values(seen=False))
    db.session.commit()
    return '', 200