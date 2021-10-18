from app import db
from app.routes import bp
from app.auth import auth


@bp.route('/users/<int:id>', methods=['DELETE'])
@auth
def delete_user(user=None):
    for item in user.items:
        db.session.delete(item)
    db.session.delete(user)
    db.session.commit()
    return {'yes': True}, 202
