from app import db
from app.routes import bp
from app.auth import auth
from app.models import User


@bp.route('/users/<int:id>', methods=['DELETE'])
@auth
def delete_user(user:User):
    for item in user.items:
        db.session.delete(item)
    db.session.delete(user)
    db.session.commit()
    return {}, 201
