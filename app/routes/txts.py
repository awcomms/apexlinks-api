import json
from flask import current_app, request
from app import db
from app.auth import auth
from app.misc.check_tags import check_tags
from app.routes import bp
from app.misc.re import re
from app.misc.cdict import cdict
from app.models.user import User, xtxts
from app.models.txt import Txt, txt_replies
from app.models import Sub
from pywebpush import webpush, WebPushException

no_auth_private_error = {
    'error': f'private txt was requested for but invalid auth token in headers'}, 400

unauthorized_to_view_error = lambda txt: {
    'error': f'you are not authorized to view txt {txt.id}'}, 401

# @bp.route('/es')
# def es():
#     return ''


@bp.route('/txts')
def get_txts():
    args = request.args.get


    txt = None
    id = args('id')
    if id:
        try:
            id = int(id)
        except:
            return {'error': 'let query arg `id` be a number'}, 400
        txt = Txt.query.get(id)
        if not txt:
            return {'error': f'txt {id} not found'}, 404
        if txt.dm or txt.personal:
            auth_user = User.check_token(request.headers.get('auth'))['user']
            if not auth_user:
                return no_auth_private_error
            if txt.dm:
                if auth_user.id not in txt.dict()['users']:
                    return unauthorized_to_view_error(txt)
            elif txt.personal:
                if txt.user.id != auth_user.id:
                    return unauthorized_to_view_error(txt)

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

    per_page = args('per_page')
    if per_page:
        try:
            per_page = int(per_page)
        except:
            return {'error': "'per-page' query arg does not seem to be a number"}, 400
    else:
        per_page = 37

    page = args('page')
    if page:
        try:
            page = int(page)
        except:
            if page != 'last':
                return {'error': "'page' query arg should be a number or the string 'last'"}, 400
    else:
        page = 'last'

    to = isinstance(args('to'), str)
    if to:
        if not txt:
            return {'error': '`to` query arg specified but no valid txt in query arg `id` specified'}
        txts = Txt.query.join(txt_replies, (txt_replies.c.txt == Txt.id)).filter(
            txt_replies.c.reply == Txt.id)

    if txt:
        txts = txt.replies
    else:
        txts = Txt.query.filter(Txt.dm == False)

    joined = isinstance(args('joined'), str)
    if joined:
        token = request.headers.get('auth')
        if not token:
            return {'error': 'query arg `join` specified. but no auth token in header field `auth`'}, 401

        authUser = User.check_token(token)['user']
        if not authUser:
            # TODO-verbose
            return {'error': 'query arg `join` specified. but invalid auth token in header `auth`'}, 401

        txts = txts.join(xtxts).filter(xtxts.c.user_id == authUser.id)

    user = args('user')
    if user:
        user = User.query.get(user)
        if not user:
            return {'error': f'user {user} specified in query arg `user` not found'}, 404
        txts = txts.filter(Txt.user_id == user.id)

    kwargs = {'txt': id}
    if tags:
        kwargs['run'] = Txt.get(tags)
    else:
        reverse = isinstance(args('reverse'), str)
        if reverse:
            txts = txts.order_by(Txt.timestamp.desc())
        else:
            txts = txts.order_by(Txt.timestamp.asc())

    print('c', txts.count())
    return cdict(txts, page, **kwargs)

@bp.route('/txts', methods=['POST'])
@auth
def post_txt(user=None):
    data = request.json.get
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
        check_tags_res = check_tags(tags, 'in request body parameter `tags`')
        if check_tags_res:
            return {'error': check_tags_res}, 400
        create_data['tags'] = tags
    t = Txt(create_data)

    id = data('txt')
    print('id', id)
    if id:
        txt = Txt.query.get(id)
        if not txt:
            return {"error": f"txt {id} specified in request body parameter `txt` not found"}, 404
        if txt.self:
            return {'error', f'txt {id} is not set to accept replies from other users'}, 400
        t.reply(txt)
        print('q', txt.id, txt.value, txt.users.all())
        db.engine.execute(xtxts.update().where(xtxts.c.user_id == user.id)
                          .where(xtxts.c.txt_id == id).values(seen=False))
        subs = Sub.query.join(User).join(
            xtxts, (xtxts.c.user_id == User.id)).filter(xtxts.c.txt_id == id).filter(User.id != user.id)
        for sub in subs:
            webpush(
                sub, data, vapid_private_key=current_app.config['VAPID'], vapid_claims={"sub": "mailto:angelwingscomms@outlook.com"})
    return t.dict(), 200

@bp.route('/txts', methods=['PUT'])
@auth
def edit_txt(user=None):

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

    personal = data('personal')
    if personal:
        if txt.dm:
            {'error': 'txt attribute `personal` may not be set for a dm txt'}, 400 #TODO
        if not isinstance(personal, bool):
            return {'error': 'let `personal` body parameter be a boolean'}

    data = {
        'value': data('value'),
        'tags': tags,
        'self': self,
        'personal': personal,
        'text': data('text')
    }

    txt.edit(data)
    return txt.dict()

@bp.route('/seen', methods=['PUT'])
@auth
def seen(user=None):
    id = request.args.get('id')
    txt = Txt.query.get(id)
    if not txt:
        return {'error': f'specified txt {id} was not found'}, 404
    db.engine.execute(xtxts.update().where(xtxts.c.user_id == user.id)
                      .where(xtxts.c.txt_id == txt.id).values(seen=True))
    return {}

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

@bp.route('/txts/dm', methods=['GET'])
@auth
def txts_dm(user=None):
    user_id = request.args.get('user')
    if not user_id:
        return {'error': "user id field `user` not specified in query parameters"}, 400
    other_user = User.query.get(user_id)
    if not other_user:
        return {'error': f'user {user_id} not found'}
    txt = None
    dm_txts = Txt.query.filter_by(dm=True)
    for t in dm_txts:
        txt_users = t.dict()['users']
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
def del_txt(id, user=None):
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
    return txt.dict()
