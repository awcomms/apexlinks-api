import json
from flask import request
from app import db
from app.routes import bp
from app.auth import auth
from app.misc.cdict import cdict
from app.relationship_tables import blogreplies
from app.models.blog import Blog
from app.models.reply import Reply
from app.models.user import User


@bp.route('/replies', methods=['GET'])
@auth
def replies(user:User):
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
            return {'error': 'unauthorized to see hidden replies for this account'}, 401
        hidden = True
    else:
        hidden = False
    try:
        tags = json.loads(a('tags'))
    except:
        tags = []
    return cdict(Reply.fuz(user_id, blog_id, hidden, tags), page)


@bp.route('/blogs/<int:id>', methods=['GET'])
def blog(id):
    return Blog.query.get(id).dict()


@bp.route('/blogs/<int:id>', methods=['DELETE'])
@auth
def del_reply(id, user:User):
    reply = Reply.query.get(id)
    if reply.user != user:
        return {}, 401
    db.session.delete(reply)
    db.session.commit()
    return {}, 201


@bp.route('/replies', methods=['POST'])
@auth
def add_reply(user:User):
    json = request.json.get
    body = json('body')
    title = json('title')
    id = json('id')

    to = json('to')
    if to:
        try:
            to = int(to)
        except:
            return {'error': "request body parameter 'to' does not seem to have a type of number"}
        to = Reply.query.get(to)
        if not to:
            return {'error': f'reply with id {to} not found'}
    blog = None
    if id:
        try:
            blog = Blog.query.get(id)
            if not blog:
                return {'error': 'blog with that id does not exist'}, 404
        except:
            return {'error': 'invalid id'}, 423
    if blog.user != user:
        return {'error': 'authenticated user does not own specified blog'}, 401
    # if Reply.query.filter(Reply.blog_id == id).filter(Reply.title == title):
    #     # TODO
    #     return {'titleError': 'A reply with that title in that blog already exists'}, 423 
    # if Reply.query.filter(Reply.blog == None).filter(Reply.title == title):
    #     return {'titleError': 'A reply that belongs to no blog with that title already exists'}, 423
    data = {
        'user': user,
        'title': title,
        'body': body,
        'blog': blog,
    }
    return {'id': Reply(data).id}


@bp.route('/replies', methods=['PUT'])
@auth
def edit_reply(user:User):
    json = request.json.get
    id = json('id')
    blog_id = json('blog')
    if id:
        try:
            id = int(id)
        except:
            return {'error': "request body parameter 'id' does not seem to have a type of number"}
        try:
            reply = Reply.query.get(id)
            if not reply:
                return {'error': 'reply with that id does not exist'}, 404
        except:
            return {'error': 'invalid id'}, 423
    else:
        return {'error': 'please provide a reply id'}, 423

    if blog_id:
        try:
            blog_id = int(blog_id)
        except:
            return {'error': "request body parameter 'blog' does not seem to have a type of number"}, 423
        blog = Blog.query.get(blog_id)
        if not blog:
            return {'error': f"blog with id {blog_id} not found"}
    else:
        blog = None

    title = json('title') # TODO-error
    # if Reply.query.filter(Reply.blog_id == id).filter(Reply.title == title):
    #     # TODO
    #     return {'titleError': 'A reply with that title in that blog already exists'}, 423
    # if Reply.query.filter(Reply.blog == None).filter(Reply.title == title):
    #     return {'titleError': 'A reply that belongs to no blog with that title already exists'}, 423 TODO-consider
    body = json('body')
    data = {
        'title': title,
        'body': body,
        'blog': blog,
    }
    reply.edit(data)
    return reply.dict(), 201
