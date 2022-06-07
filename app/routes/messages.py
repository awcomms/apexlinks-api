from flask import request
from app.routes import bp
from app import db
from app.auth import auth
from app.misc.cdict import cdict
from app.models.user import User, xrooms
from app.models.room import Room
from app.models.message import Message


@bp.route('/messages')
def get_messages():
    messages = Message.query
    args = request.args.get
    model = args('model')
    mode = args('mode')
    per_page = args('per_page')
    page = args('page')
    id = args('id')
    # TODO-error

    if id:
        try:
            id = int(id)
        except:
            return {'error': 'id should have a type of number'}
    else:
        pass  # TODO-error

    if per_page:
        try:
            per_page = int(per_page)
        except:
            return {'error': "'per-page' query arg does not seem to be a number"}
    else:
        per_page = 100

    if page:
        try:
            page = int(page)
        except:
            if page != 'last':
                return {'error': "'page' query arg should be a number or the string 'last'"}
    else:
        page = 'last'

    if model == 'message':
        message = Message.query.get(id)
        if not message:
            return {'error': f'message {id} not found'}, 404
        if mode == 'single':
            return message.dict()
        if mode == 'replies':
            messages = Message.query.get(id).replies
        if mode == 'messages':
            messages = Message.query.get(id).messages
    elif model == 'room':
        messages = Room.query.get(id).messages

    messages = messages.order_by(Message.timestamp.asc())

    n_pages = 0

    if page == 'last':
        pages = messages.paginate(1, per_page)
        n_pages = pages.pages
        while pages.page != n_pages:
            pages = pages.next()
        page = pages.page
    else:
        pages = messages.paginate(page, per_page, False)
        n_pages = pages.pages
    messages = pages.items

    # TODO-search

    return cdict(messages, page, n_pages)


@bp.route('/messages', methods=['POST'])
@auth
def post_message(user=None):
    data = request.json.get
    id = data('room')
    room = Room.query.get(id)
    if not room:
        return {"error": f"room {id} not found"}, 404
    value = data('value')
    m = Message(value, user, room)
    db.engine.execute(xrooms.update().where(
        xrooms.c.room_id == room.id).values(seen=False))
    db.session.commit()
    return m.dict(), 200
