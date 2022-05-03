from app.models import Item
from flask import Response, abort

def remove_items(item, json, _arg):
    arg = f'remove-{_arg}'
    ids = json(arg)
    if ids:
        for id in ids:
            if id:
                try:
                    id = int(id)
                except:
                    abort(400, Response({'error': f"{id} in request body parameter {arg} does not seem to be a JSON number type"}))

                second_item = Item.query.get(id)
                if not second_item:
                    abort(400, Response(
                        {'error': f'item with id {id} not found'}))

                if arg == 'parents':
                    second_item.remove_item(item)
                elif arg == 'children':
                    item.remove_item(second_item)
            else:
                pass
                # TODO-error

def add_items(item, json, arg):
    ids = json(arg)
    print('add ids', ids)
    if ids:
        for id in ids:
            if id:
                try:
                    id = int(id)
                except:
                    abort(400, Response({'error': f"{id} in request body parameter {arg} does not seem to be a JSON number type"}))
                    
                second_item = Item.query.get(id)
                print('sec', second_item)
                if not second_item:
                    abort(400, Response({'error': f'item with id {id} not found'}))
                if arg == 'parents':
                    second_item.add_item(item)
                elif arg == 'children':
                    item.add_item(second_item)
            else:
                pass
                # TODO-error
