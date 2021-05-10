from flask import request
from app.api import bp
from app import db
from app.misc import cdict
from app.user_model import User
from app.room_model import Room
from app.message_model import Message

@bp.route('/messages', methods=['GET'])
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

@bp.route('/messages', methods=['POST'])
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
    for user in room.users:
        if not room.id in user.in_rooms:
            if not room.id in user.unseen_rooms:
                user.unseen_rooms.append(room.id)
    db.session.commit()
    return '', 200