from app.auth import auth
from flask import request
from app.misc.check_include import check_include
from app.routes import bp
from app.models.user import User


@bp.route('/user')
@auth
def get_auth_user(user=None):
    if user:
        include = request.args.get('include')
        try:
            include = check_include(include)
        except Exception as e:
            return e.args[0]
        return user.dict(include=include)
    else:
        return '', 400


@bp.route('/users/<username>')
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": f"user with username `{username}` not found"}, 404
    return user.dict()


@bp.route('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if user:
        include = request.args.get('include')
        if include:
            try:
                include = check_include(include)
            except Exception as e:
                print('sdi', type(e.args), e.args[0])
                return e.args[0]
        return user.dict(include=include)
    else:
        return {'error': f'user with id {id} was not found'}, 404
