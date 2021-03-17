from flask import request
from app import bp
from app.user_models import User
from app.group_models import Group
from app.message_models import Message

@bp.route('/messages', methods=['POST'])
def post_message():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user: return '', 401
    data = request.json.get
    id = data('id')
    group = Group.query.get(id)
    if not group:
        return '', 404
    body = data('body')
    Message(body, user, group)

