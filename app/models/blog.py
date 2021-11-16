from sqlalchemy.orm import backref
from app import db
from fuzzywuzzy import process, fuzz
from app.models.user import User
from app.relationship_tables import blogs
from app.relationship_tables import posts

class Blog(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blogs = db.relationship('Blog', secondary='blogs',
            primary_join=(blogs.c.parent_id == id),
            secondary_join=(blogs.c.child_id == id),
            backref=db.backref('blog', lazy='dynamic'), lazy='dynamic')
    posts = db.relationship('Post', secondary='blogposts', backref=db.backref('blog', lazy='dynamic'),
            lazy='dynamic')
    hidden = db.Column(db.Boolean, default=False)
    data = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    body = db.Column(db.Unicode)
    score = db.Column(db.Float)

    def post_added(self, post):
        return self.posts.filter(posts.c.child_id == self.id).count > 0

    def add_post(self, post):
        if not self.blog_added(post):
            self.blogs.append(post)
            db.session.commit()

    def remove_post(self, post):
        if self.post_added(post):
            self.posts.remove(post)
            db.session.commit()

    def blog_added(self, blog):
        return self.blogs.filter(blogs.c.child_id == self.id).count > 0

    def add_blog(self, blog):
        if not self.blog_added(blog):
            self.blogs.append(blog)
            db.session.commit()
    
    def remove_blog(self, blog):
        if self.blog_added(blog):
            self.blogs.remove(blog)
            db.session.commit()

    @staticmethod
    def fuz(id, hidden, tags):
        query = Blog.query.join(User)
        if not id:
            query = query.filter(User.hidden==False)
        elif id:
            query=query.filter(User.id==id)
        try:
            query=query.filter(Blog.hidden==hidden)
        except:
            pass
        for blog in query:
            blog.score = 0
            for tag in tags:
                try:
                    blog.score += process.extractOne(tag, blog.tags)[1]
                except:
                    pass
        db.session.commit()
        query.order_by(Blog.score.desc())
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