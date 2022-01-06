from flask_socketio import send, emit, join_room, leave_room
from app.models import Room, User, Message
from app.models.user import xrooms
from app import db, socket

@socket.on('join')
def join(data):
    user = User.query.get(data['user'])
    room = Room.query.get(data['room'])
    user.join(room)
    join_room(data['room'])

@socket.on('leave')
def leave(data):
    user = User.query.get(data['user'])
    room = Room.query.get(data['room'])
    user.leave(room)
    leave_room(data['room'])

@socket.on('msg')
def msg(data):
    room = Room.query.get(data['id'])
    user = User.query.get(data['user'])
    # if not user TODO-error
    # if not room TODO-error
    value = data['value']
    msg = Message(value, user, room)
    db.engine.execute(xrooms.update().where(xrooms.c.room_id==room.id).values(seen=False))
    db.session.commit()
    emit('msg', msg.dict(), to=room)