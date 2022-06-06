from app.auth import auth
from app.routes import bp
from flask import request
from app.misc.cdict import cdict
from app.models.user import User

@bp.route('/user')
@auth
def __user(user=None):
    if user:
        return user.dict()
    else:
        return '', 400

@bp.route('/users/<int:id>', methods=['GET'])
def _user(id):
    user = User.query.get(id)
    # _extra = {}
    # saved_users = request.args.get('saved_users')
    # saved_items = request.args.get('saved_items')
    # user = User.query.filter_by(username=username).first()
    if user:
        return user.dict()
        # if saved_users:
        #     _extra['saved_users'] = cdict(user.saved_users)
        # if saved_items:
        #     _extra['saved_items'] = cdict(user.saved_items)
        # return user.dict(_extra=_extra)
    else:
        return {'error': f'user with id {id} was not found'}, 404
