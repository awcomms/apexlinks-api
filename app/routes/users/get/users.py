from app.auth import auth

import json
from flask import request
from app.routes import bp
from app.misc.check_include import check_include
from app.misc.sort.tag_sort import tag_sort
from app.models.user import User
from app.misc.cdict import cdict

@bp.route('/users', methods=['GET'])
def users(user:User):
    a = request.args.get
    extraFields = a('extraFields')
    limit = a('limit')
    if limit:
        try:
            limit = int(limit)
        except:
            return {'error': "'limit' query arg should be a number"}
    else:
        limit = 0
    sort = a('sort')
    print('sort', sort)
    if sort:
        if sort != 'tag' and sort != 'distance':
            return {'error': "sort query arg should be 'tag' or 'distance'"}
    else:
        sort = 'tag'
    loc = a('loc')

    include = a('include')
    try:
        include = check_include(include, 'query arg')
    except Exception as e:
        return e.args[0]

    # if loc:
    #     try:
    #         loc = json.loads(loc)
    #         if not isinstance(loc, dict):
    #             return {'error': 'loc query arg should be an object'}, 400
    #     except:
    #         return {'error': 'loc query arg should be a stringified JSON object'}, 400
    #     if not 'lon' in loc:
    #         return {'error': "not 'lat' in loc"}, 400
    #     if not 'lon' in loc:
    #         return {'error': "not 'lon' in loc"}, 400
    #     try:
    #         loc['lat'] = float(loc['lat'])
    #     except:
    #         return {'error': 'lat property in loc query arg should be a float'}, 400
    #     try:
    #         loc['lon'] = float(loc['lon'])
    #     except:
    #         return {'error': 'lon property in loc query arg should be a float'}, 400

    # try:
    #     extraFields = json.loads(extraFields)
    #     if not isinstance(extraFields, list):
    #         return {'error': 'extraFields query arg should be a stringified json list of objects'}
    # except:
    #     return {'error': 'extraFields query arg should be a stringified json list of objects'}
    
    # fields = a('fields')
    # try:
    #     fields = json.loads(fields)
    #     if not isinstance(fields, list):
    #         return {'error': 'fields query arg should be a stringified json list of objects'}
    # except:
    #     return {'error': 'fields query arg should be a stringified json list of objects'}
   
    tags = a('tags')
    if tags:
        try:
            tags = json.loads(tags)
            if not isinstance(tags, list):
                return {'error': "tags query arg is doesn't seem to be of a list type"}
        except:
            tags = []
    else:
        tags = []
    try:
        page = int(a('page'))
    except:
        page = 1
    
    query = User.query.filter_by(hidden=False)
    
    run = lambda items: tag_sort(items, tags)
    return cdict(query, page, run=run, include=include)