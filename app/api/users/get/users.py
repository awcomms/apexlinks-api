import json
from flask import request
from app.api import bp
from app.user_model import User
from app.misc.cdict import cdict

@bp.route('/users', methods=['GET'])
def users():
    a = request.args.get
    id = a('id')
    user = None
    try:
        id = int(id)
    except:
        id = None
    if id:
        user = User.query.get(id)
        if user:
            return user.dict()
        else:
            return {'error': f'user with id {id} not found'}
    try:
        tags = json.loads(a('tags'))
        if not isinstance(tags, list):
            return {'error': "tags query arg is doesn't seem to be of a list type"}
    except:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1
    return cdict(User.get(tags), page)