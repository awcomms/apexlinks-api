import hmac
import hashlib
from app.api import bp
from app.models import Card, User
from flask import current_app

@bp.route('/del_card', methods=['PUT'])
def del_card():
    j = request.json.get
    token = request.headers['Authorization']
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    card = Card.query.get(j('id'))
    if not card:
        return jsonify('error': 'card does not exist')
    db.session.delete(card)
    db.session.commit()
    return {}, 202

@bp.route('/ref', methods=['POST'])
def ref():
    current_app.logger.info('got_payed')
    key = current_app.config['PAYSTACK']
    sign = hmac.new(key, request.data, hashlib.sha512).hexdigest()
    req_sign = request.headers['X-Paystack-Signature']
    if sign == req_sign:
        _dict = request.json()
        id = _dict['data']['metadata']['id']
        user = User.query.get(id)
        authorization_code = _dict['data']['authorization']['authorization_code']
        if not user.cards.filter(User.card.authorization_code == authorizatiion_code):
            card = Card(_dict['data']['authorization'])
            card.user = user
            db.session.commit()
        user.subscribed = True
