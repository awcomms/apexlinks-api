import json
from app import db
from app.misc.items.edit import edit
from app.misc.items.set_items import add_items, remove_items
from app.misc.sort.tag_sort import tag_sort
from app.routes import bp
from app.misc.cdict import cdict
from app.auth import auth
from app.models.user import User
from app.models.item import Item, item_items
from flask import request


@bp.route('/items', methods=['GET'], endpoint='items')
def items(user=None):
    a = request.args.get

    user = User.check_token(request.headers.get('token'))['user']

    sort = request.args.get('sort')
    limit = request.args.get('limit')
    
    saved = request.args.get('saved')

    query = Item.query
    parent_query = None
    child_query = None
    
    parent_ids = request.args.get('parent-ids')
    if parent_ids:
        print('parent-ids', parent_ids)
        try:
            parent_ids = json.loads(parent_ids)
        except:
            return {'error': "query arg 'parent-id' does not seem to be a stringified JSON object"}, 400
        if not isinstance(parent_ids, list):
            return {'error': "query arg 'parent-id' does not seem to be a JSON list"}, 400

        for id in parent_ids:
            try:
                id = int(id)
            except:
                return {'error': f'{id} in request body parameter "parent-ids" does not seem to be a number'}, 400
            parent_query = query.join(item_items, item_items.c.child == Item.id).filter(item_items.c.parent == id)

    child_ids = request.args.get('child-ids')
    print('children-ids', child_ids)
    if child_ids:
        try:
            child_ids = json.loads(child_ids)
        except:
            return {'error': "query arg 'child-id' does not seem to be a stringified JSON object"}, 400
        if not isinstance(child_ids, list):
            return {'error': "query arg 'child-id' does not seem to be a JSON list"}, 400

        for id in child_ids:
            try:
                id = int(id)
            except:
                return {'error': f'{id} in request body parameter "child-ids" does not seem to be a number'}, 400
            child_query = query.join(item_items, item_items.c.parent == Item.id).filter(
                item_items.c.child == id)

    if parent_query:
        if child_query:
            print('pcq', query.count())
            query = parent_query.union(child_query)
        else:
            print('pcqx', query.count())
            query = parent_query
    elif child_query:
        print('pcs', query.count())
        query = child_query

    market_id = a('market-id')
    if market_id:
        try:
            market_id = int(market_id) #TODO #error_check
        except:
            return {'error': "query arg 'market-id does not seem have a type of number"}

    user_id = a('user-id')
    if user_id:
        try:
            user_id = int(user_id)
        except:
            return {'error': "query arg 'user-id' doesn't seem to have a type of number"}
        try:
            _user = User.query.get(user_id)
            if not _user:
                return {'error': 'User not found'}, 404
            if _user.hidden:
                return {'error': 'User hidden'}, 423
        except:
            return {'error': "query arg 'user-id' doesn't seem to have a type of number"}, 400
    
    page = a('page')
    if page:
        try:
            page = int(page)
        except:
            return {'error': f"'page' query arg does not seem to have a type of number"}

    hidden = a('hidden')
    if hidden and user:
        hidden = True
    else:
        hidden = False
    
    tags = a('tags')
    if tags:
        try:
            tags = json.loads(tags)
        except Exception as e:
            print('tags route items error: ', e)
            return {'error': "'tags' query arg does not seem to be a stringified list"}
    else:
        tags = []
    market_id = None

    if market_id:
        query = query.filter(User.market_id == market_id)

    query = query.join(User)
    if user_id:
        print('user_id', user_id)
        query = query.filter(User.id == user_id)

    if user and user.id == user_id:
        try:
            query = query.filter(Item.hidden == hidden)
        except:
            pass  # TODO-error
    else:
        print('eqs', query.count())
        query = query.filter(User.hidden == False)
        print('eqs', query.count())
        # query = query.filter(Item.hidden == False)
        print('eqs', query.count())
    print('qs', query.count())

    run = lambda items: tag_sort(items, tags)

    # _items = [i.dict(user=user, attrs=['saved']) for i in query]
    # print('.__items', items)
    # _items = run(_items)
    # return { 'items': _items, 'total': len(_items)}
    return cdict(query, page, user=user, run=run, attrs=['saved'])

@bp.route('/items', methods=['POST'])
@auth
def add_item(user=None):
    json = request.json.get

    item = edit(json, user, new=True)

    return {'id': item.id}, 202


@bp.route('/items', methods=['PUT'])
@auth
def edit_item(user=None):
    json = request.json.get
    
    item = edit(json, user)
    
    return {'id': item.id}


@bp.route('/items/<int:id>', methods=['GET'])
def item(id):
    try:
        id = int(id)
    except:
        return {'error': 'Invalid id type'}, 400
    return Item.query.get(id).dict()

@bp.route('/items/<int:id>', methods=['DELETE'])
@auth
def del_item(id, user=None):
    item = Item.query.get(id)

    if item.user != user:
        return '', 401

    db.session.delete(item)
    db.session.commit()
    return {'yes': True}
