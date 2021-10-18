import json
from app import db
from app.routes import bp
from app.misc import cdict
from app.user_model import User
from app.blog_model import Blog
from flask import request
from flask_jwt_extended import jwt_required


@bp.route('/blogs', methods=['GET'])
def blogs():
    a = request.args.get
    id = a('id')
    if id:
        user = User.query.get(id)
        if not user:
            return {}, 404
        if user.hidden:
            return {}, 423
    page = int(a('page'))
    itype = a('itype')
    hidden = a('hidden')
    if hidden == 'true':
        hidden = True
    elif hidden == 'false':
        hidden = False
    else:
        hidden = True
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    return cdict(Blog.fuz(id, hidden, itype, tags), page)


@bp.route('/blogs', methods=['POST'])
def add_blog():
    token = request.headers.get('token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return '401', 401
    json = request.json.get
    name = json('name')
    itype = json('itype')
    price = json('price')
    if Blog.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another blog owned by same user has that name'}
    tags = json('tags') or []
    tags.append(name)
    tags.append(price)
    data = {
        'name': name,
        'itype': itype,
        'itext': json('itext'),
        'hidden': json('hidden'),
        'images': json('images'),
        'image': json('image'),
        'price': price,
        'user': user,
        'tags': tags
    }
    # if tags:
    #     for field in data:
    #         i = data[field]
    #         if not i in tags:
    #             tags.append(i)
    i = Blog(data)
    return {'id': i.id}


@bp.route('/blogs', methods=['PUT'])
def edit_blog():
    token = request.headers.get('token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    json = request.json.get
    id = json('id')
    blog = Blog.query.get(id)
    name = json('name')
    itype = json('itype')
    price = json('price')
    if name != blog.name and Blog.query.filter_by(itype=itype)\
        .filter_by(user_id=user.id)\
            .filter_by(name=name).first():
        return {'nameError': 'Another blog owned by same user has that name'}, 400
    tags = json('tags') or []
    if blog and blog.user != user:
        return {}, 401
    tags.append(name)
    tags.append(price)
    data = {
        'name': name,
        'itext': json('itext'),
        'hidden': json('hidden'),
        'images': json('images'),
        'itype': json('itype'),
        'image': json('image'),
        'price': price,
        'tags': tags
    }
    # if tags:
    #     for field in data:
    #         i = data[field]
    #         if not i in tags:
    #             tags.append(i)
    blog.edit(data)
    return {'id': blog.id}


@bp.route('/blogs/<int:id>', methods=['GET'])
def blog(id):
    return Blog.query.get(id).dict()


@bp.route('/blogs/<int:id>', methods=['DELETE'])
def del_blog(id):
    token = request.headers.get('token')
    user = User.query.filter_by(token=token).first()
    if not user:
        return {}, 401
    blog = Blog.query.get(id)
    if blog.user != user:
        return {}, 401
    db.session.delete(blog)
    db.session.commit()
    return {'yes': True}
