from flask import jsonify, abort
from app.models import Item
from app.misc.items.set_items import add_items, remove_items
from app import db


def edit(json, user, new=False):
    if new:
        item = Item(now=False, edit=False)
    else:
        id = json('id')
        if not id:
            print('no id')
            return {'error': 'required request body parameter "id" seems unavailable or empty'}
        item = Item.query.get(id)
        if not item:
            print('not found')
            abort(400, jsonify({'error': 'item does not exist'}))
        if item.user.id != user.id:
            abort(401, jsonify({'error': "item does not belong to user"}))

    tags = json('tags')
    if not isinstance(tags, list):
        print('tags not list')
        abort(400, jsonify(
            {'error': 'request body parameter "tags" does not seem to be a JSON "list" type'}))

    fields = json('fields')
    if not isinstance(fields, list):
        print('fields not list')
        abort(400, jsonify(
            {'error': 'request body parameter "fields" does not seem to be a JSON "list" type'}))

    data = {
        'hidden': json('hidden'),
        'redirect': json('redirect'),
        'images': json('images'),
        'options': json('options'),
        'choices': json('choices'),
        'image': json('image'),
        'link': json('link'),
        'fields': fields,
        'user': user,
        'tags': tags
    }

    item.edit(data)

    add_items(item, json, 'parents')
    add_items(item, json, 'children')

    remove_items(item, json, 'parents')
    remove_items(item, json, 'children')

    db.session.commit()
    return item
