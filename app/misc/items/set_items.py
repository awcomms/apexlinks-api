from app.models import Item
from flask import Response, abort, jsonify


def remove_items(item, json, _arg):
    arg = f'remove-{_arg}'
    ids = json(arg)
    if ids:
        for idx, id in enumerate(ids):
            if id:
                try:
                    id = int(id)
                except:
                    print(f'remove {_arg} id not number')
                    abort(400, jsonify(
                        {'error': f"{id} in request body parameter {arg} does not seem to be a JSON number type"}))

                second_item = Item.query.get(id)
                if not second_item:
                    print('not found')
                    abort(400, jsonify({'error': f'item with id {id} not found'}))

                if arg == 'parents':
                    second_item.remove_item(item)
                elif arg == 'children':
                    item.remove_item(second_item)
            else:
                return {'error': f'let item at index {idx} in request body parameter {arg} not be a null value'}

def add_items(item, json, arg):
    ids = json(arg)
    print('add ids', ids)
    if ids:
        for idx, id in enumerate(ids):
            if id:
                try:
                    id = int(id)
                except:
                    print('add id not number')
                    abort(400, jsonify(
                        {'error': f"{id} in request body parameter {arg} does not seem to be a JSON number type"}))

                second_item = Item.query.get(id)
                if not second_item:
                    print('not found')
                    abort(400, jsonify(
                        {'error': f'item with id {id} not found'}))
                if arg == 'parents':
                    second_item.add_item(item)
                elif arg == 'children':
                    item.add_item(second_item)
            else:
                return {'error': f'let item at index {idx} in request body parameter {arg} not be a null value'}