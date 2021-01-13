import hmac
import hashlib
from app.api import bp
from pypaystack import Customer, Transaction
from app.models import User
from flask import current_app

@bp.route('/charge', methods=['PUT'])
def charge():
    a = request.args.get
    u_id = a('u_id')
    user = User.query.get('u_id')
    key = current_app.config['PAYSTACK']
    transaction = Transaction(authorization_key=key)
    transaction.charge(user.email, user.card[authorization_code], 210)
    user.subscribed = True
    return jsonify({'yes': True})


@bp.route('/ref', methods=['POST'])
def ref():
    key = current_app.config['PAYSTACK']
    customer = Customer(authorization_key=key)
    current_app.logger.info('got_payed')
    sign = hmac.new(key, request.data, hashlib.sha512).hexdigest()
    req_sign = request.headers['X-Paystack-Signature']
    if sign == req_sign:
        _dict = request.json()
        id = _dict['data']['metadata']['id']
        user = User.query.get(id)
        _customer = customer.getone(user.customer_code)
        if not _customer:
            customer.create(user.email)
        authorization_code = _dict['data']['authorization']['authorization_code']
        if user.card[authorization_code] != authorization_code:
            user.card = _dict['data']['authorization']
        user.subscribed = True
        db.session.commit()