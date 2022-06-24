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
            return {'error': 'id does not seem to be a number'}, 400
        txt = Txt.query.get(id)
        if not txt:
            return {'error': f'txt {id} not found'}, 404

    if per_page:
        try:
            per_page = int(per_page)
        except:
            return {'error': "'per-page' query arg does not seem to be a number"}, 400
    else:
        per_page = 100

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
        txts = Txt.query.filter_by(dm=False).join(txt_replies, txt_replies.c.txt == Txt.id).filter(txt_replies.c.reply != Txt.id)

    txts = txts.order_by(Txt.timestamp.asc())

    # n_pages = 0
    # if page == 'last':
    #     pages = txts.paginate(1, per_page)
    #     n_pages = pages.pages
    #     while pages.page != n_pages:
    #         pages = pages.next()
    #     page = pages.page
    # else:
    #     pages = txts.paginate(page, per_page, False)
    #     n_pages = pages.pages
    # txts = pages.items

    def run(items):
        for item in items:
            item_tags = []
            words = item.value.split(' ') #TODO trim double spaces
            phrases = []
            for word in words:
                phrases.push(word)
                phrase = word + words
        pass
    # TODO-search

    return cdict(txts, page, 0, txt=id)

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
    request_data = request.json.get
    user_id = request_data('user')
    if not user_id:
        return {'error': "user id field `user` not provided in query parameters"}, 400
    other_user = User.query.get(user_id)
    if not other_user:
        return {'error': f'user {user_id} not found'}
    user_txts = db.session.query(Txt.id).join(xtxts).filter(xtxts.c.user_id == user.id)
    other_user_txts = r = db.session.query(Txt).join(
        xtxts).filter(xtxts.c.user_id == 2)
    both_users_txts = other_user_txts.filter(Txt.id.in_(user_txts))
    txt = both_users_txts.filter(Txt.dm == True).first()
    if not txt:
        txt = Txt({'dm': True})
        user.join(txt)
        other_user.join(txt)
    return txt.dict(), 201

@bp.route('/txts', methods=['POST'])
@auth
def add_txt(user=None):
    data = request.json.get
    name = data('name')
    tags = data('tags') or []
    data = {
        'name': name,
        'user': user,
        'tags': tags,
        'about': data('about')
    }
    txt = Txt(data)
    user.join(txt)
    return {'id': txt.id}

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
        'name': data('name'),
        'tags': tags,
        'about': data('about')
    }

    txt.edit(data)

    return {'id': txt.id}

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
