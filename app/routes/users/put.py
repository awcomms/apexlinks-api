from app.misc.fields.check_and_clean import check_and_clean
from app.email import send_reset_password
import json
from flask import request
from app.routes import bp
from app.auth import auth
from app.models import Item, User
from app.models.market import Market


@bp.route('/users/activate')
@auth
def activate_user():
    id = request.json.get('id')
    User.activate(id)
    return '', 200


@bp.route('/forgot_password', methods=['PUT'])
def forgot_password():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            'error': True,
            'usernameInvalid': True,
            'usernameError': 'No user with that username'
        }, 401
    if user.email:
        send_reset_password(user)
    else:
        return {'r': 'No email set for this user'}, 404
    return {'r': 'Check for an email'}


@bp.route('/reset_password', methods=['PUT'])
def reset_password():
    token = request.headers.get('token')
    password = request.json.get('password')
    user = User.check_reset_password_token(token)
    if user:
        user.set_password(password)
        return {'r': True}
    else:
        return {}


@bp.route('/users', methods=['PUT'])
@auth
def edit_user(user=None):
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
    attrs = ['about', 'settings', 'hiddden', 'images', 'image', 'tags']

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

    market_id = request_json('market_id')
    if market_id:
        try:
            market_id = int(market_id)
            market = Market.query.get(market_id)
            if not market:
                return {'error': f'market with id {market_id} not found'}
        except:
            return {'error': 'market_id should be an int'}
        data['market'] = market

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

    tags = request_json('tags') or []
    if type(tags) != list:
        try:
            tags = json.loads(tags)
            if not isinstance(tags, list):
                return {'error': f'let tags request body parameter be of a list type'}
            for tag in tags:
                if not isinstance(tag, str):
                    return {'error': f'let tag {tag} be of a string type'}
        except SyntaxError or TypeError:
            tags = tags.split(',')
        except SyntaxError or TypeError:
            tags = tags.split(';')
        except SyntaxError or TypeError:
            return 'Unsupported tags format', 415
    user.edit(data)

    return user.dict(_extra=_extra)
