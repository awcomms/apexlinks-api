from flask import request, current_app
from app.routes import bp
from app.auth import auth
from app.models.sub import Sub
from app.models.txt import Txt
from app.models.user import User, xtxts

@bp.route('/subs', methods=['POST'])
@auth
def post_sub(user=None):
    sub = request.json.get('sub')
    # existing_sub = Sub.query.filter(Sub.sub['endpoint'].as_string() == sub['endpoint']).first()
    # if existing_sub:
    #     print('existing')
    #     existing_sub.sub = sub
    #     return existing_sub.sub, 200
    s = Sub(user, sub)
    return s.sub, 201

@bp.route('/subs', methods=['GET'])
def get_subs():
    args = request.args.get
    id = int(args('id'))
    if args('key') != current_app.config['KEY']:
        return '401', 401
    if not Txt.query.get(id):
        return '404', 404
    subs = Sub.query.join(User).join(xtxts, (xtxts.c.user_id == User.id))\
        .filter(xtxts.c.txt_id == id).all()
    return {'subs': [s.sub for s in subs]}
    