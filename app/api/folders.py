from flask import request
from app.user_model import User
from app.folder_model import Folder
from app.api import bp

@bp.route('/folders', methods=['POST'])
def add_folder():
    token = request.headers.get('token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    name = request.json.get('name')
    folder = Folder(name, user)
    return {'id': folder.id}

@bp.route('/folders', methods=['PUT'])
def edit_folder():
