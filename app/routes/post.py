import json
from flask import request
from app import db
from app.routes import bp
from app.auth import auth
from app.misc.cdict import cdict
from app.relationship_tables import blogposts
from app.model.blog import Blog
from app.models.post import Post
from app.models.user import User


@bp.route('/posts', methods=['GET'])
@auth(optional=True)
def posts(user=None):
    a = request.args.get
    user_id = a('user_id')
    req_user = None
    if user_id:
        try:
            req_user = User.query.get(user_id)
            if not req_user:
                return {}, 404
        except:
            return {'error': 'invalid user_id'}, 423
    authed = user == req_user
    if req_user and req_user.hidden and not authed:
        return {'error': 'user hidden'}, 403
    blog_id = a('blog_id')
    if blog_id:
        try:
            blog = Blog.query.get(blog_id)
            if not blog:
                return {}, 404
            if blog.hidden and user != blog.user:
                return {'error': 'blog hidden'}, 403
        except:
            return {'error': 'invalid blog_id'}, 423
    page = int(a('page'))
    hidden = a('hidden')
    if hidden == '1':
        if not authed:
            return {'error': 'unauthorized to see hidden posts for this account'}, 401
        hidden = True
    else:
        hidden = False
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    return cdict(Post.fuz(user_id, blog_id, hidden, tags), page)


@bp.route('/blogs/<int:id>', methods=['GET'])
def blog(id):
    return Blog.query.get(id).dict()


@bp.route('/blogs/<int:id>', methods=['DELETE'])
@auth
def del_post(id, user=None):
    post = Post.query.get(id)
    if post.user != user:
        return {}, 401
    db.session.delete(post)
    db.session.commit()
    return {}, 202


@bp.route('/posts', methods=['POST'])
@auth
def add_post(user=None):
    json = request.json.get
    body = json('body')
    title = json('title')
    id = json('id')
    blog = None
    if id:
        try:
            blog = Blog.query.get(id)
            if not blog:
                return {'error': 'blog with that id does not exist'}, 404
        except:
            return {'error': 'invalid id'}, 423
    if blog.user != user:
        return {}, 401
    if Post.query.filter(Post.blog_id == id).filter(Post.title == title):
        # TODO
        return {'titleError': 'A post with that title in that blog already exists'}, 423
    if Post.query.filter(Post.blog == None).filter(Post.title == title):
        return {'titleError': 'A post that belongs to no blog with that title already exists'}, 423
    data = {
        'user': user,
        'title': title,
        'body': body,
        'blog': blog,
    }
    return {'id': Post(data).id}


@bp.route('/posts', methods=['PUT'])
@auth
def edit_post(user=None):
    json = request.json.get
    id = json('id')
    if id:
        try:
            post = Post.query.get(id)
            if not post:
                return {'error': 'post with that id does not exist'}, 404
        except:
            return {'error': 'invalid id'}, 423
    else:
        return {'error': 'please provide a post id'}, 423
    title = json('title')
    if Post.query.filter(Post.blog_id == id).filter(Post.title == title):
        # TODO
        return {'titleError': 'A post with that title in that blog already exists'}, 423
    if Post.query.filter(Post.blog == None).filter(Post.title == title):
        return {'titleError': 'A post that belongs to no blog with that title already exists'}, 423
    body = json('body')
    data = {
        'title': title,
        'body': body,
    }
    post.edit(data)
    return {}, 202
