import json
from app.vars.q import default_user_fields
from flask import request
from app.routes import bp
from app.misc.sort.tag_sort import tag_sort
from app.models.user import User
from app.misc.cdict import cdict

@bp.route('/users', methods=['GET'])
def users():
    a = request.args.get
    extraFields = a('extraFields')
    market_id = a('market_id')
    sort = a('sort')
    print('sort', sort)
    if sort:
        if sort != ('tag' or 'distance'):
            return {'error': "sort query arg should be 'tag' or 'distance'"}
    loc = a('loc')
    if loc:
        try:
            loc = json.loads(loc)
            if not isinstance(loc, dict):
                return {'error': 'loc query arg should be an object'}, 400
        except:
            return {'error': 'loc query arg should be a stringified JSON object'}, 400
        if not 'lon' in loc:
            return {'error': "not 'lat' in loc"}, 400
        if not 'lon' in loc:
            return {'error': "not 'lon' in loc"}, 400
        try:
            loc['lat'] = float(loc['lat'])
        except:
            return {'error': 'lat property in loc query arg should be a float'}, 400
        try:
            loc['lon'] = float(loc['lon'])
        except:
            return {'error': 'lon property in loc query arg should be a float'}, 400
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
    run = lambda items: tag_sort(default_fields, items, tags)
    return cdict(User.get(sort, tags, loc), page, run)