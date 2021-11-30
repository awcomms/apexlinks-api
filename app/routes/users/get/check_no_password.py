from app.routes import bp
from app.models.user import User


@bp.route('/users/check-no-password/<username>')
def check_no_password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': f'user {username} not found'}, 404
    return {'res': user.no_password}
