from sqlalchemy.orm import backref
from app import db
from fuzzywuzzy import process, fuzz
from app.user_model import User
from app.blog_model import Blog
from app.relationship_tables import posts

class Post(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    posts = db.relationship('Post', secondary='posts',
            primary_join=(posts.c.parent_id ==id),
            secondary_join=(posts.c.child_id ==id),
            backref=db.backref('post', lazy='dynamic'), lazy='dynamic')
    posts = db.relationship
    hidden = db.Column(db.Boolean, default=False)
    data = db.Column(db.Unicode)
    title = db.Column(db.Unicode)
    post = db.relationship('Post', backref='user', lazy='dynamic')
    score = db.Column(db.Float)

    def post_added(self, post):
        return self.posts.filter(posts.c.child_id == post.id).count > 0

    def add_post(self, post):
        if not self.blog_added(post):
            self.blogs.append(post)
            db.session.commit()

    def remove_post(self, post):
        if self.post_added(post):
            self.posts.remove(post)
            db.session.commit()

    @staticmethod
    def fuz(user_id, blog_id, hidden, tags):
        query = Post.query.join(Blog).join(User)
        query=query.filter(Post.hidden==hidden)
        if user_id:
            query=query.filter(Blog.user_id==user_id)
        if blog_id:
            query=query.filter(Blog.blog_id==blog_id)
        for post in query:
            post.score = 0
            for tag in tags:
                try:
                    post.score += process.extractOne(tag, post.tags)[1]
                except:
                    pass
        db.session.commit()
        query.order_by(Post.score.desc())
        return query

    def dict(self, **kwargs):
       return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'body': self.body,
            'hidden': self.hidden,
            'user': self.user.username
        }

    def __init__(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.add(self)
        db.session.commit()

    def edit(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.commit()