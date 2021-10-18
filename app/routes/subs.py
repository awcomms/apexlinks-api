import json
from flask import request
# from flask_cors import cross_origin
from app import db
from app.routes import bp
from app.sub_model import Sub
from app.room_model import Room
from app.user_model import User


@bp.route('/subs', methods=['POST'])
# @cross_origin(origins=['http://localhost:3000', 'https://apexlinks.org','https://x369.herokuapp.com'])
def post_sub():
    data = request.json.get
    id = data('id')
    user = User.query.get(id)
    if not user or user.subs.first():
        return {}
    sub = data('sub')
    endpoint = sub['endpoint']
    if Sub.query.filter(Sub.endpoint == endpoint).first():
        return {}
    Sub(user, endpoint, sub)
    return {}, 201


@bp.route('/subs/<id>', methods=['GET'])
# @cross_origin(origins=['http://localhost:3000', 'https://x369.live','https://x369.herokuapp.com'])
def get_subs(id):
    if not Room.query.get(id):
        return {}
    subs = Sub.query.join(User).join(Room).filter(Room.id == id)
    return {'subs': [s.sub for s in subs]}
