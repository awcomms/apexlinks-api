import json
from app import db
from app.misc.sort.tag_sort import tag_sort
from app.routes import bp
from app.misc.cdict import cdict
from app.auth import auth
from app.models.user import User
from app.models.item import Item
from flask import request


@bp.route('/items', methods=['GET'], endpoint='items')
def items(user=None):
    a = request.args.get

    user = User.check_token(request.headers.get('token'))['user']

    # sort = request.args.get('sort')
    saved = request.args.get('saved')

    parent_ids = request.args.get('parent_ids')
    if parent_ids:
        for id in parent_ids:
            try:
                int(id)
            except:
                return {'error': f'{id} in body parameter "parent_ids" does not seem to be a number'}

    market_id = a('market_id')
    if market_id:
        market_id = int(market_id) #TODO #error_check

    user_id = a('user_id')
    if user_id:
        try:
            user_id = int(user_id)
        except:
            return {'error': "query arg 'user_id' doesn't seem to have a type of number"}
        try:
            _user = User.query.get(user_id)
            if not _user:
                return {'error': 'User not found'}, 404
            if _user.hidden:
                return {'error': 'User hidden'}, 423
        except:
            return {'error': 'Invalid id type'}, 400
    
    page = a('page')
    if page:
        try:
            page = int(page)
        except:
            return {'error': f"'page' query arg does not seem to have a type of number"}
    hidden = a('hidden')
    if hidden == 'true':
        hidden = True
    elif hidden == 'false':
        hidden = False
    else:
        hidden = True
    
    print('.__here')
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
    query = Item.query.join(User)

    
    # if market_id:
    #     query = query.filter(User.market_id == market_id)

    if user_id:
        query = query.filter(User.id == user_id)

    if user and user.id == id:
        try:
            query = query.filter(Item.hidden == hidden)
        except:
            pass  # TODO-error
    else:
        query = query.filter(User.hidden == False)
        query = query.filter(Item.hidden == False)

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
    print(json('itype'))
    tags = json('tags') or []
    fields = json('fields')

    parent_item_ids = json('parent_items')
    parent_items = []
    for item_id in parent_item_ids:
        if item_id:
            try:
                item_id = int(item_id)
            except:
                return {'error': f"body param 'id' does not seem to have a type of number"}
            parent_item = Item.query.get(item_id)
            if not parent_item:
                return {'error': f'item with id {item_id} not found'}
            parent_items.append(parent_item)

    child_item_ids = json('child_items')
    child_items = []
    for item_id in child_item_ids:
        if item_id:
            try:
                item_id = int(item_id)
            except:
                return {'error': f"body param 'id' does not seem to have a type of number"}
            child_item = Item.query.get(item_id)
            if not child_item:
                return {'error': f'item with id {item_id} not found'}
            child_items.append(child_item)

    
    item_id = json('item')
    if item_id:
        try:
            item_id = int(item_id)
        except:
            return {'error': f"body param 'id' does not seem to have a type of number"}
        item = Item.query.get(item_id)
        if not item:
            return {'error': f'item with id {item_id} not found'}

    data = {
        'hidden': json('hidden'),
        'redirect': json('redirect'),
        'images': json('images'),
        'fields': fields,
        'image': json('image'),
        'link': json('link'),
        'item': item,
        'user': user,
        'tags': tags
    }
    item = Item(data)
    for parent in parent_items:
        parent.add_item(item)
    for child in child_items:
        item.add_item(child)
    db.session.commit()
    return {'id': item.id}


@bp.route('/items/<int:id>', methods=['PUT'])
@auth
def edit_item(id, user=None):
    json = request.json.get
    item = Item.query.get(id)

    parent_item_ids = json('parent_items')
    parent_items = []
    for item_id in parent_item_ids:
        if item_id:
            try:
                item_id = int(item_id)
            except:
                return {'error': f"body param 'id' does not seem to have a type of number"}
            parent_item = Item.query.get(item_id)
            if not parent_item:
                return {'error': f'item with id {item_id} not found'}
            parent_items.append(parent_item)

    child_item_ids = json('child_items')
    child_items = []
    for item_id in child_item_ids:
        if item_id:
            try:
                item_id = int(item_id)
            except:
                return {'error': f"body param 'id' does not seem to have a type of number"}
            child_item = Item.query.get(item_id)
            if not child_item:
                return {'error': f'item with id {item_id} not found'}
            child_items.append(child_item)


    if not item:
        return {'error': 'item does not exist'}, 404
    if item and item.user.id != user.id:
        return {'error': "item does not belong to user"}, 403
    name = json('name')
    itype = json('itype')
    if name != item.name and Item.query\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Author already has item with same name'}, 400
    
    tags = json('tags') or []
    
    if name and name not in tags:
        tags.append(name)
    
    if itype and itype not in tags:
        tags.append(itype)
    
    data = {
        'itext': json('itext'),
        'hidden': json('hidden'),
        'images': json('images'),
        'image': json('image'),
        'link': json('link'),
        'price': json('price'),
        'fields': json('fields'),
        'redirect': json('redirect'),
        'itype': itype,
        'name': name,
        'tags': tags
    }
    
    for parent in parent_items:
        parent.add_item(item)
    for child in child_items:
        item.add_item(child)
    db.session.commit()

    item.edit(data)
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
        return {}, 401
    db.session.delete(item)
    db.session.commit()
    return {'yes': True}
