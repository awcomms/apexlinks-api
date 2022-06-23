from flask import request, current_app
from app.routes import bp
from app.models.sub import Sub
from app.models.txt import Txt
from app.models.user import User, xtxts

@bp.route('/subs', methods=['POST'])
def post_sub():
    data = request.json.get
    id = data('id')
    user = User.query.get(id)
    if not user or user.subs.first():
        return ''
    sub = data('sub')
    if Sub.query.filter(Sub.sub['endpoint'] == sub['endpoint']):
        return ''
    Sub(user, sub)
    return '', 201

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
    