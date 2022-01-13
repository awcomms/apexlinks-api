from app.routes import bp
from flask import request
from app.misc.cdict import cdict
from app.models.user import User

@bp.route('/users/<username>', methods=['GET'])
def _user(username):
    _extra = {}
    saved_users = request.args.get('saved_users')
    saved_items = request.args.get('saved_items')
    user = User.query.filter_by(username=username).first()
    if user:
        if saved_users:
            _extra['saved_users'] = cdict(user.saved_users)
        if saved_items:
            _extra['saved_items'] = cdict(user.saved_items)
        return user.dict(_extra=_extra)
    else:
        return {'error': f'user {username} was not found'}, 404
