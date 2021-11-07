from flask import request
from app.models.user import User
from app.folder_model import Folder
from app.routes import bp


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
