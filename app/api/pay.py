import hmac
import hashlib
from app.api import bp
from flask import current_app

@bp.route('/payed', methods=['POST'])
def payed():
    key = current_app.config['PAYSTACK_KEY']
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
        user.visible = True
