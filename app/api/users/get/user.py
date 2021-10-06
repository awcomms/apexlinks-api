from app.api import bp
from app.user_model import User

@bp.route('/users/<username>', methods=['GET'])
def _user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user.dict()
    else:
        return {'error': f'user {username} was not found'}