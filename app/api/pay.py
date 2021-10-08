import hmac
import hashlib
from app.email import send_renewal_failure
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from flask import request
from flask import current_app
from pypaystack import Transaction
from app.user_model import User
from app.api import bp
from app import db

@bp.route('/pay/check', methods=['GET'])
def check():
    test = current_app.config['PAYSTACK_TEST']
    test_key = current_app.config['PAYSTACK_TEST_KEY']
    live_key = current_app.config['PAYSTACK_LIVE_KEY']
    key = test_key if test == 'True' else live_key
    transaction = Transaction(token_key=key)
    duration = timedelta(days=30)
    for user in User.query:
        if user.last_paid + duration > datetime.now(timezone.utc):
            user.paid = False
            res = transaction.charge(user.card['email'], auth_code=user.card['token_code'], amount=190233)
            if res[3]['metadata']['purpose'] != 'change_card' and res[3]['status'] == 'success':
                user.paid = True
            else:
                send_renewal_failure(user)
    db.session.commit()

@bp.route('/pay', methods=['POST'])
def pay():
    print('/pay')
    test = current_app.config['PAYSTACK_TEST']
    test_key = current_app.config['PAYSTACK_TEST_KEY']
    live_key = current_app.config['PAYSTACK_LIVE_KEY']
    key = test_key if test == 'True' else live_key
    data = request.get_json()
    if not request.data:
        return '', 400
    hash = hmac.new(key, request.data, digestmod=hashlib.sha512).hexdigest()
    request_hash = request.headers.get('X-Paystack-Signature')
    if not hmac.compare_digest(hash, request_hash):
        return {}
    user = User.query.get(data.metadata.id) 
    user.card = data['data']['token']
    print(data['data']['token']['email'])
    print(data['event'])
    user.paid = True
    user.last_paid = datetime.now(timezone.utc)
    db.session.commit()
    return {}, 200

@bp.route('/pay/is_paid', methods=['GET'])
def is_paid():
    test = current_app.config['PAYSTACK_TEST']
    test_key = current_app.config['PAYSTACK_TEST_KEY']
    live_key = current_app.config['PAYSTACK_LIVE_KEY']
    key = test_key if test == 'True' else live_key
    ref = request.args.get('ref')
    transaction = Transaction(token_key=key)
    res = transaction.verify(ref)
    if res[3]['status'] == 'success':
        return {'res': True}
    else:
        return {'res': False}
