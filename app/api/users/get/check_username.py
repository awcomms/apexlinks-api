from app.api import bp
from app.user_model import User

#returns `False` if username exists
@bp.route('/check_username/<username>', methods=['GET'])
def check_username(username):
    return {'res': User.query.filter_by(username=username).count()<1}
