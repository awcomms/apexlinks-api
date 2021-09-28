import hmac
import hashlib
from app.email import send_renewal_failure
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from flask import request
from flask import current_app
from pypaystack import Transaction, transactions
from app.user_model import User
from app.api import bp
from app import db

@bp.route('check', methods=['GET'])
def check():
    key = current_app.config.PAYSTACK
    transaction = Transaction(token_key=key)
    duration = timedelta(days=30)
    for user in User:
        if user.last_paid + duration > datetime.now(timezone.utc):
            user.paid = False
            res = transaction.charge(user.card['email'], auth_code=user.card['token_code'], amount=190233)
            if res[3]['metadata']['purpose'] != 'change_card' and res[3]['status'] == 'success':
                user.paid = True
            else:
                send_renewal_failure(user)
    db.session.commit()

@bp.route('paid', methods=['POST'])
def paid():
    key = current_app.config.PAYSTACK
    data = request.get_json()
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

@bp.route('is_paid', methods=['GET'])
def is_paid():
    ref = request.args.get('ref')
    key = current_app.config.PAYSTACK
    transaction = Transaction(token_key=key)
    res = transaction.verify(ref)
    if res[3]['status'] == 'success':
        return {'res': True}
    else:
        return {'res': False}
