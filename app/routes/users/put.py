from app.misc.check_tags import check_tags
from app.misc.fields.check_and_clean import check_and_clean
import json
from flask import request
from app.routes import bp
from app.auth import auth
from app.models import Item, User

@bp.route('/users/activate')
@auth
def activate_user():
    id = request.json.get('id')
    User.activate(id)
    return '', 200

@bp.route('/users', methods=['PUT'])
@auth
def edit_user(user:User):
    _extra = {}
    request_json = request.json.get
    data_request_json = request.get_json()

    save_users = request_json('save_toggle_users')
    if save_users:
        users_save_toggled = []
        for idx, id in enumerate(save_users):
            print(id)
            try:
                id = int(id)
            except:
                return {'error': f"query arg 'id' does not seem to have a type of id"}, 400
            _user = User.query.get(id)
            if not _user:
                return {'error': f'user {id} not found'}, 404
            user.save_toggle_user(_user)
            users_save_toggled.append(_user.dict(user=user, attrs=['saved']))
        _extra['users_save_toggled'] = users_save_toggled

    save_items = request_json('save_toggle_items')
    if save_items:
        items_save_toggled = []
        for idx, id in enumerate(save_items):
            try:
                id = int(id)
            except:
                return {'error': f"query arg 'id' does not seem to have a type of id"}, 400
            item = Item.query.get(id)
            if not item:
                return {'error': f'item {id} not found'}, 400
            user.save_toggle_item(item)
            items_save_toggled.append(item.dict(user=user, attrs=['saved']))
        _extra['items_save_toggled'] = items_save_toggled

    data = {}
    attrs = ['text', 'options', 'settings', 'hidden', 'images', 'image', 'online']

    for attr in attrs:
        if attr in data_request_json:
            data[attr] = request_json(attr)

    username = request_json('username')
    if username:
        if username == '':
            return {'error': 'No username'}, 400
        if username != user.username and \
                User.query.filter_by(username=username).first():
            return {'error': 'Username taken'}, 400
        data['username'] = username

    fields = request_json('fields')
    if fields:
        if not isinstance(fields, list):
            return {'error': 'let fields request body parameter be of a list type'}
        for idx, field in enumerate(fields):
            res = check_and_clean(field)
            if isinstance(res, str):
                return {'error': res}
            fields[idx] = res
        data['fields'] = fields

    tags = request_json('tags')
    check_tags_res = check_tags(tags, 'query body parameter `tags`')
    if check_tags_res:
        return {'error': check_tags_res}, 400
    data['tags'] = tags
    user.edit(data)

    return user.dict(_extra=_extra)
