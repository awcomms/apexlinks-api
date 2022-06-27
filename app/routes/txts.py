import json
from flask import request
from app import db
from app.auth import auth
from app.misc.check_tags import check_tags
from app.routes import bp
from app.misc.cdict import cdict
from app.models.user import User, xtxts
from app.models.txt import Txt
from app.models.txt import txt_replies

@bp.route('/txts')
def get_txts():
    args = request.args.get

    per_page = args('per_page')
    page = args('page')
    id = args('id')

    txt = None
    if id:
        try:
            id = int(id)
        except:
            return {'error': 'query arg `id` does not seem to be a number'}, 400
        txt = Txt.query.get(id)
        if not txt:
            return {'error': f'txt {id} not found'}, 404

    tags = args('tags')
    if tags:
        tags_error_prefix = 'value in query arg `tags` '
        try:
            tags = json.loads(tags)
        except:
            return {'error': f'{tags_error_prefix}does not seem tob be a stringified JSON object'}
        tags_error = check_tags(tags, tags_error_prefix)
        if tags_error:
            return {'error', tags_error}

    if per_page:
        try:
            per_page = int(per_page)
        except:
            return {'error': "'per-page' query arg does not seem to be a number"}, 400
    else:
        per_page = 37

    if page:
        try:
            page = int(page)
        except:
            if page != 'last':
                return {'error': "'page' query arg should be a number or the string 'last'"}, 400
    else:
        page = 'last'

    if txt:
        txts = txt.replies
    else:
        txts = Txt.query.filter_by(dm=False)

    kwargs = {'txt': id}
    if tags:
        kwargs['run'] = Txt.get(tags)
    else:
        txts = txts.order_by(Txt.timestamp.asc())

    return cdict(txts, page, **kwargs)

@bp.route('/txts', methods=['POST'])
@auth
def post_txt(user=None):
    data = request.json.get
    create_data = {
        'value': data('value'),
        'user': user,
    }
    tags = data('tags')
    if tags:
        check_tags_res = check_tags(tags, 'in request body parameter `tags`')
        if check_tags_res:
            return {'error': check_tags_res}
        create_data['tags'] = tags
    t = Txt(create_data)

    id = data('txt')
    if id:
        txt = Txt.query.get(id)
        if not txt:
            return {"error": f"txt {id} specified in request body parameter `txt` not found"}, 404
        t.reply(txt)
    return t.dict(), 200

@bp.route('/txts', methods=['PUT'])
@auth
def edit_txt(user=None):
    data = request.json.get
    id = data('id')
    txt = Txt.query.get(id)
    if not txt:
        return {"error": f"txt {id} not found"}
    tags = data('tags')
    check_tags_res = check_tags(tags, 'request body parameter `tags`')
    if check_tags_res:
        return {"error": check_tags_res}
    if txt.user.id != user.id:
        return {"error": "authenticated user did not create this txt"}, 401
    data = {
        'value': data('value'),
        'name': data('name'),
        'tags': tags,
        'about': data('about')
    }

    txt.edit(data)
    return txt.dict()


@bp.route('/seen', methods=['PUT'])
@auth
def seen(user=None):
    id = request.args.get('id')
    txt = Txt.query.get(id)
    if not txt:
        return '404', 404
    db.engine.execute(xtxts.update().where(xtxts.c.user_id == user.id)
                      .where(xtxts.c.txt_id == txt.id).values(seen=True))
    return '201', 201

@bp.route('/join/<int:id>', methods=['PUT'])
@auth
def join(id, user=None):
    txt = Txt.query.get(id)
    if not txt:
        return {"error": f"txt {id} not found"}, 404
    user.join(txt)
    return {}, 201

@bp.route('/leave/<int:id>', methods=['PUT'])
@auth
def leave(id, user=None):
    txt = Txt.query.get(id)
    if not txt:
        return {"error": f"txt {id} not found"}, 404
    user.leave(txt)
    return {}, 201

@bp.route('/xtxts', methods=['GET'])
@auth
def get_xtxts(user=None):
    query = Txt.query
    args = request.args.get

    query = query.join(xtxts).filter(xtxts.c.user_id == user.id)

    try:
        tags = json.loads(args('tags'))
    except:
        tags = []

    try:
        page = int(args('page'))
    except:
        page = 1

    run = Txt.get(tags)
    return cdict(query, page, run=run)

@bp.route('/txts/users', methods=['POST'])
@auth
def txts_users(user=None):
    print(user)
    request_data = request.json.get
    user_id = request_data('user')
    if not user_id:
        return {'error': "user id field `user` not provided in query parameters"}, 400
    other_user = User.query.get(user_id)
    if not other_user:
        return {'error': f'user {user_id} not found'}
    txt = None
    dm_txts = Txt.query.filter_by(dm=True)
    for t in dm_txts:
        txt_users = t.dict()['users']
        if user.id in txt_users and other_user.id in txt_users:
            txt = t
    # user_txts = db.session.query(Txt.id).join(xtxts).filter(xtxts.c.user_id == user.id)
    # other_user_txts = db.session.query(Txt).join(
    #     xtxts).filter(xtxts.c.user_id == 2)
    # both_users_txts = other_user_txts.filter(Txt.id.in_(user_txts))
    # txt = both_users_txts.filter(Txt.dm == True).first()
    statusCode = 200
    if not txt:
        txt = Txt({'dm': True})
        user.join(txt)
        other_user.join(txt)
        statusCode = 201
    return txt.dict(), statusCode

@bp.route('/txts/<int:id>', methods=['DELETE'])
@auth
def del_txt(id, user=None):
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'txt {id} not found'}, 404
    if txt.user != user:
        return {'error': 'authenticated user was not owner of specified txt'}, 401
    db.session.delete(txt)
    db.session.commit()
    return '', 200

@bp.route('/txts/<int:id>', methods=['GET'])
def get_txt_by_id(id):
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'txt {id} not found'}, 404
    return txt.dict(include_tags=True)
