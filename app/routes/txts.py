import json
from flask import current_app, request
from app import db
from app.auth import auth, maybe_auth
from app.misc.check_include import check_include
from app.misc.check_tags import check_tags
from app.routes import bp
from app.misc.re import re
from app.misc.cdict import cdict
from app.models.user import User, xtxts
from app.models.txt import Txt, txt_replies
from app.models import Sub
from pywebpush import webpush
from threading import Thread

def send_notifications(app, txt):
    with app.app_context():
        s = Sub.query.join(xtxts, xtxts.c.user_id ==
                           Sub.user_id).filter(xtxts.c.txt_id == txt.id)
        for sub in Sub.query:
            try:
                webpush(
                    sub.sub, json.dumps({'id': txt.id}), vapid_private_key=current_app.config['VAPID'], vapid_claims={"sub": "mailto:angelwingscomms@outlook.com"})
            except:
                pass


no_auth_private_error = {
    'error': f'private txt was requested for but invalid auth token in headers'}, 400


def unauthorized_to_view_error(txt): return {
    'error': f'you are not authorized to view txt {txt.id}'}, 401

# @bp.route('/es')
# def es():
#     return ''

@bp.route('/txts/to')
@maybe_auth
def get_txts_to(user:User):
    args = request.args.get

    id = args('id')
    if id:
        try:
            id = int(id)
        except:
            return {'error': 'let query arg `id` be an integer'}
    else:
        return {'error': 'query arg id not specified'}

    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'txt {id} not found'}, 404

    page = args('page')
    if page:
        try:
            page = int(page)
        except:
            return {'error': 'let query arg `page` be a number'}
    else:
        page='last'

    kwargs = {'include': ['user', 'value'], 'page': page}
    if user:
        kwargs['include'].append('seen')
        kwargs['user'] = user

    query = Txt.query.join(txt_replies, txt_replies.c.txt == Txt.id).filter(txt_replies.c.reply == txt.id)
    print(query.all())
    return cdict(query, **kwargs)

@bp.route('/txts')
@maybe_auth
def get_txts(user:User):
    args = request.args.get

    txt: Txt | None = None

    limit = args('limit')
    id = args('id')
    tags = args('tags')
    per_page = args('per_page')
    page = args('page')
    to = isinstance(args('to'), str)
    joined = isinstance(args('joined'), str)
    dm = isinstance(args('dm'), str)
    personal = isinstance(args('personal'), str)
    append = isinstance(args('append'), str)

    if to:
        if not txt:
            return {'error': '`to` query arg specified but no valid txt in query arg `id` specified'}

    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {'error': 'let query arg `limit` be an integer'}, 400
        except:
            return {'error': 'unknown error while parsing query arg `limit`. make sure query arg `limit` is a number'}, 400

    if id:
        try:
            id = int(id)
        except:
            return {'error': 'let query arg `id` be a number'}, 400
        txt = Txt.query.get(id)
        if not txt:
            return {'error': f'txt {id} not found'}, 404
        if txt.dm or txt.personal:
            auth_user: User | None = User.check_token(request.headers.get('auth'))['user']
            if not auth_user:
                return no_auth_private_error
            if txt.dm:
                if auth_user.id not in txt.dict()['users']:
                    return unauthorized_to_view_error(txt)
            elif txt.personal:
                if txt.user.id != auth_user.id:
                    return unauthorized_to_view_error(txt)

    if tags:
        tags_error_prefix = 'query arg `tags`'
        try:
            tags = json.loads(tags)
        except:
            return {'error': f'{tags_error_prefix}does not seem tob be a stringified JSON object'}, 400
        tags_error = check_tags(tags, tags_error_prefix)
        if tags_error:
            return {'error': tags_error}, 400

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
        if to:
            txts = Txt.query.join(txt_replies, (txt_replies.c.txt == Txt.id)).filter(
                txt_replies.c.reply == txt.id)
        else:
            txts = Txt.query.join(txt_replies, (txt_replies.c.reply == Txt.id)).filter(
                txt_replies.c.txt == txt.id)
    else:
        txts = Txt.query

    if joined:
        token = request.headers.get('auth')
        if not token:
            return {'error': 'query arg `join` specified. but no auth token in header field `auth`'}, 401

        if not user:
            # TODO-verbose
            return {'error': 'query arg `join` specified. but invalid auth token in header `auth`'}, 401

        txts = txts.join(xtxts).filter(xtxts.c.user_id == user.id)

    req_user = args('user')
    if req_user:
        req_user = User.query.get(req_user)
        if not req_user:
            return {'error': f'user {req_user} specified in query arg `user` not found'}, 404
        txts = txts.filter(Txt.user_id == req_user.id)

    include = args('include')
    try:
        include = check_include(include, 'query arg')
    except Exception as e:
        return e.args[0]

    kwargs = {'include': include, 'user': user, 'limit': limit, 'append': append}
    if txt: kwargs['txt'] = txt.id

    if tags:
        kwargs['run'] = Txt.get(tags)
    else:
        reverse = isinstance(args('reverse'), str)
        if txt: table = txt_replies.c
        else: table = Txt
        if reverse:
            txts = txts.order_by(table.time.desc())
        else:
            txts = txts.order_by(table.time.asc())

    print('c', txts.count())
    return cdict(txts, page, **kwargs)


@bp.route('/txts', methods=['POST'])
@auth
def post_txt(user):
    data = request.json.get

    # include = request.args.get('include')
    # try:
    #     include = check_include(include)
    # except Exception as e:
    #     return e.args[0]

    dm = data('dm')
    if dm:
        if not isinstance(dm, bool):
            return {'error': 'let query body parameter `dm` be a boolean'}
    create_data = {
        'value': data('value'),
        'text': data('text'),
        'dm': dm,
        'user': user,
    }
    tags = data('tags')
    if tags:
        check_tags_res = check_tags(tags, 'request body parameter `tags`')
        if check_tags_res:
            return {'error': check_tags_res}, 400
        create_data['tags'] = tags
    t = Txt(create_data)

    include: list = ['user', 'value']

    id = data('txt')
    if id:
        txt: Txt = Txt.query.get(id)
        if not txt:
            return {"error": f"txt {id} specified in request body parameter `txt` not found"}, 404
        if txt.self and (not user or txt.user.id != user.id):
            return {'error', f'txt {id} is not set to accept replies from other users'}, 400
        include.append('joined')
        t.reply(txt)
        db.engine.execute(xtxts.update().where(xtxts.c.txt_id == id).values(seen=False))
        Thread(target=send_notifications, args=(current_app._get_current_object(), txt))        
    return t.dict(include=include, user=user), 200

@bp.route('/txts', methods=['PUT'])
@auth
def edit_txt(user:User):

    data = request.json.get

    id = data('id')
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'txt {id} not found'}, 404

    if txt.user.id != user.id:
        return {"error": "authenticated user did not create this txt"}, 401

    reply_re_res = re(data, txt, 'reply')
    if reply_re_res:
        return reply_re_res
    unreply_re_res = re(data, txt, 'unreply')
    if unreply_re_res:
        return unreply_re_res

    include = request.args.get('include')
    try:
        include = check_include(include)
    except Exception as e:
        return e.args[0]

    tags = data('tags')
    if tags:
        check_tags_res = check_tags(tags, 'request body parameter `tags`')
        if check_tags_res:
            return {"error": check_tags_res}, 400

    self = data('self')
    if self:
        if txt.dm:
            {'error': 'txt attribute `self` may not be set for a dm txt'}, 400  # TODO
        if not isinstance(self, bool):
            return {'error': 'let `self` body parameter be a boolean'}

    anon = data('anon')
    if anon:
        if not isinstance(anon, bool):
            return {'error': f'let query body parameter `anon` be a boolean'}

    personal = data('personal')
    if personal:
        if txt.dm:
            {'error': 'txt attribute `personal` may not be set for a dm txt'}, 400  # TODO
        if not isinstance(personal, bool):
            return {'error': 'let `personal` body parameter be a boolean'}

    text = data('text')
    print(f'{txt.id} text', text)

    data = {
        'value': data('value'),
        'tags': tags,
        'self': self,
        'anon': anon,
        'personal': personal,
        'text': data('text')
    }

    txt.edit(data)
    return txt.dict(include)


@bp.route('/seen', methods=['PUT'])
@auth
def seen(user:User):
    id = request.args.get('id')
    if not id:
        return {'error': 'provide query arg `id`'}
    try:
        id = int(id)
    except:
        return {'error': 'let query arg `id` be a number'}
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'specified txt {id} was not found'}, 404
    db.engine.execute(xtxts.update().where(xtxts.c.user_id == user.id)
                      .where(xtxts.c.txt_id == txt.id).values(seen=True))
    return {}


@bp.route('/join/<int:id>', methods=['PUT'])
@auth
def join(id, user:User):
    txt = Txt.query.get(id)
    if not txt:
        return {"error": f"txt {id} not found"}, 404
    user.join(txt)
    return {'joined': user.in_txt(txt)}

@bp.route('/leave/<int:id>', methods=['PUT'])
@auth
def leave(id, user:User):
    txt = Txt.query.get(id)
    if not txt:
        return {"error": f"txt {id} not found"}, 404
    user.leave(txt)
    return {'joined': user.in_txt(txt)}

@bp.route('/txts/dm', methods=['GET'])
@auth
def txts_dm(user:User):
    user_id = request.args.get('user')
    if not user_id:
        return {'error': "user id field `user` not specified in query parameters"}, 400
    other_user = User.query.get(user_id)
    if not other_user:
        return {'error': f'user {user_id} not found'}
    txt = None
    dm_txts = Txt.query.filter_by(dm=True)
    for t in dm_txts:
        txt_users = t.dict(include=['users'])['users']
        if (user.id in txt_users) and (other_user.id in txt_users):
            txt = t
    # user_txts = db.session.query(Txt.id).join(xtxts).filter(xtxts.c.user_id == user.id)
    # other_user_txts = db.session.query(Txt).join(
    #     xtxts).filter(xtxts.c.user_id == 2)
    # both_users_txts = other_user_txts.filter(Txt.id.in_(user_txts))
    # txt = both_users_txts.filter(Txt.dm == True).first()
    statusCode = 200
    if not txt:
        txt = Txt({'dm': True})
        print(txt.id)
        user.join(txt)
        other_user.join(txt)
        statusCode = 201
    print('a', txt.id, txt.value, txt.users.all())
    return txt.dict(), statusCode


@bp.route('/txts/<int:id>', methods=['DELETE'])
@auth
def del_txt(id, user:User):
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'txt {id} not found'}, 404
    if txt.user != user:
        return {'error': 'authenticated user was not owner of specified txt'}, 401
    db.session.delete(txt)
    db.session.commit()
    return {}, 200


@bp.route('/txts/<int:id>', methods=['GET'])
def get_txt_by_id(id):
    txt = Txt.query.get(id)
    token = request.headers.get('auth')
    user = User.check_token(token)['user']
    if not txt:
        return {'error': f'txt {id} not found'}, 404
    if txt.personal or txt.dm:
        if not user:
            return no_auth_private_error

        if txt.personal:
            if user.id != txt.user.id:
                return unauthorized_to_view_error(txt)
        elif txt.dm:
            print(txt.dict())
            if user.id not in txt.dict()['users']:
                return unauthorized_to_view_error(txt)

    include = request.args.get('include')
    try:
        include = check_include(include)
    except Exception as e:
        return e.args[0]
    return txt.dict(include=include, user=user)
