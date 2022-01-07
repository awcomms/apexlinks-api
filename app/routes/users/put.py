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
    request_json = request.json.get

    save_users = request_json('save_users')
    for id, idx in enumerate(save_users):
        try:
            id = int(id)
        except:
            return {'error': f"query arg 'id' does not seem to have a type of id"}
        _user = User.query.get(id)
        if not _user:
            return {'error': f'user {id} not found'}
        user.save_user(user)

    save_items = request_json('save_items')
    for id, idx in enumerate(save_items):
        try:
            id = int(id)
        except:
            return {'error': f"query arg 'id' does not seem to have a type of id"}
        item = Item.query.get(id)
        if not item:
            return {'error': f'item {id} not found'}
        user.save_item(user)

    data = {
        'address': request_json('address'),
        'website': request_json('website'),
        'phone': request_json('phone'),
        'location': request_json('location'),
        'email': request_json('email'),
        'name': request_json('name'),
    }
    username = request_json('username')
    if not username or username == '':
        return {'usernameInvalid': True, 'usernameError': 'No username'}, 400
    if username and username != user.username and \
            User.query.filter_by(username=username).first():
        return {'usernameInvalid': True, 'usernameError': 'Username taken'}, 400
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
            return {'error': 'let fields body param be of a list type'}
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
                return {'error': f'let tags body parameter be of a list type'}
            for tag in tags:
                if not isinstance(tag, str):
                    return {'error': f'let tag {tag} be of a string type'}
        except SyntaxError or TypeError:
            tags = tags.split(',')
        except SyntaxError or TypeError:
            tags = tags.split(';')
        except SyntaxError or TypeError:
            return 'Unsupported tags format', 415

    data['show_email'] = request_json('show_email')
    data['about'] = request_json('about')
    data['hidden'] = request_json('hidden')
    data['location'] = request_json('location')
    data['images'] = request_json('images')
    data['image'] = request_json('image')
    data['tags'] = tags
    user.edit(data)
    return user.dict()