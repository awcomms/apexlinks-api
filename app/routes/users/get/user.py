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
    if user:
        return user.dict()
    else:
        return {'error': f'user with id {id} was not found'}, 404
