import json
from app import db, socket
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
def items():
    a = request.args.get

    same_user = False
    auth_user = User.check_token(request.headers.get('token'))['user']

    query = Item.query.join(User).filter(User.hidden == False)

    user = a('user')
    if user:
        try:
            user = int(user)
        except:
            return {'error': "query arg 'user' does not seem to be a number"}
        
        user = User.query.get(user)
        if not user:
            return {'error': f'User {user} not found'}, 404
        if user.hidden:
            return {'error': 'User {user} is hidden'}, 423  # TODO-words

        query = query.filter(User.id == user.id)

        same_user = auth_user.id == user.id

    sort = request.args.get('sort')
    limit = request.args.get('limit')
    saved = request.args.get('saved')

    parent = request.args.get('parent')
    print('parent', parent)
    child = request.args.get('child')
    print('child', child)

    parent_query = None
    child_query = None
    parents_query = None
    children_query = None

    if not parent == None:
        parent_query = query.join(item_items, item_items.c.parent == Item.id)
    if not child == None:
        child_query = query.join(item_items, item_items.c.child == Item.id)

    if parent_query:
        print('z', parent_query.count())
        if child_query:
            print('ez', child_query.count())
            query = parent_query.union(child_query)
        else:
            print('zee', parent_query.count())
            query = parent_query
    elif child_query:
        print('c', child_query.count())
        query = child_query
    
    parents = request.args.get('parents')
    if parents:
        print('parent-ids', parents)
        try:
            parents = json.loads(parents)
        except:
            return {'error': "query arg 'parent-id' does not seem to be a stringified JSON object"}, 400
        if not isinstance(parents, list):
            return {'error': "query arg 'parent-id' does not seem to be a JSON list"}, 400

        for id in parents:
            try:
                id = int(id)
            except:
                return {'error': f'{id} in request body parameter "parent-ids" does not seem to be a number'}, 400
            parents_query = query.join(item_items, item_items.c.child == Item.id).filter(item_items.c.parent == id)

    children = request.args.get('children')
    print('children', children)
    if children:
        try:
            children = json.loads(children)
        except:
            return {'error': "query arg 'child-id' does not seem to be a stringified JSON object"}, 400
        if not isinstance(children, list):
            return {'error': "query arg 'child-id' does not seem to be a JSON list"}, 400

        for id in children:
            try:
                id = int(id)
            except:
                return {'error': f'{id} in request body parameter "child-ids" does not seem to be a number'}, 400
            children_query = query.join(item_items, item_items.c.parent == Item.id).filter(
                item_items.c.child == id)

    if parents_query:
        if children_query:
            print('pcq', query.count())
            query = parents_query.union(children_query)
        else:
            print('pcqx', query.count())
            query = parents_query
    elif children_query:
        print('pcs', query.count())
        query = children_query

    market_id = a('market-id')
    if market_id:
        try:
            market_id = int(market_id) #TODO #error_check
        except:
            return {'error': "query arg 'market-id does not seem have a type of number"}
        query = query.filter(User.market_id == market_id)

    page = a('page')
    if page:
        try:
            page = int(page)
        except:
            return {'error': f"'page' query arg does not seem to be a number"}

    tags = a('tags')
    if tags:
        try:
            tags = json.loads(tags)
        except Exception as e:
            print('tags route items error: ', e)
            return {'error': "'tags' query arg does not seem to be a stringified JSON list"}
        if not isinstance(tags, list):
            return {'error': "'tags' query arg does not seem to be a stringified JSON list"}
    else:
        tags = []

    # hidden = a('hidden')
    # if hidden:
    #     if same_user:
    #         if hidden == 'include':
    #             query = query.union(query.filter(Item.hidden == True))
    #         else:
    #             query = query.filter(Item.hidden == True)
    #     else:
    #         return {'error': 'query arg "hidden" was specified yet client is not authenticated as user specified in query arg "user"'}
    # else:
    #     query = query.filter(Item.hidden == False)
        
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
    socket.emit('add', item.dict())

    return item.dict(), 202

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
