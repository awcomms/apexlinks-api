from flask import request
from app.routes import bp
from app.user_model import User


@bp.route('/check_reset_password_token', methods=['GET'])
def check_reset_password_token():
    token = request.headers.get('token')
    if User.check_reset_password_token(token):
        return {'r': True}
    else:
        return {}
