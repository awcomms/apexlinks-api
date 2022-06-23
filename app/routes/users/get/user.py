from app.auth import auth
from app.routes import bp
from flask import request
from app.misc.cdict import cdict
from app.models.user import User

@bp.route('/user')
@auth
def get_auth_user(user=None):
    if user:
        return user.dict()
    else:
        return '', 400

@bp.route('/users/<username>')
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": f"user with username `{username}` not found"}, 404
    return user.dict(include_tags=True)

@bp.route('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if user:
        return user.dict(include_tags=True)
    else:
        return {'error': f'user with id {id} was not found'}, 404
