import json
from flask import request
from app.routes import bp
from app.models.user import User
from app.misc.cdict import cdict


@bp.route('/users', methods=['GET'])
def users():
    a = request.args.get
    extraFields = a('extraFields')
    market_id = a('market_id')
    if market_id:
        market_id = int(market_id) #TODO #error_check
    try:
        extraFields = json.loads(extraFields)
        if not isinstance(extraFields, list):
            return {'error': 'extraFields query arg should be a stringified json list of objects'}
    except:
        return {'error': 'extraFields query arg should be a stringified json list of objects'}
    
    fields = a('fields')
    try:
        fields = json.loads(fields)
        if not isinstance(fields, list):
            return {'error': 'fields query arg should be a stringified json list of objects'}
    except:
        return {'error': 'fields query arg should be a stringified json list of objects'}
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
    return cdict(User.get(market_id, extraFields, tags, fields), page)
