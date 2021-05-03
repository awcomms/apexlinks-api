from sqlalchemy.orm import backref
from app import db
from fuzzywuzzy import process, fuzz
from app.user_model import User

class Blog(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visible = db.Column(db.Boolean, default=True)
    data = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    post = db.relationship('Post', backref='user', lazy='dynamic')
    score = db.Column(db.Float)

    @staticmethod
    def fuz(id, visible, tags):
        query = Blog.query.join(User)
        if not id:
            query = query.filter(User.visible==True)
        elif id:
            query=query.filter(User.id==id)
        try:
            query=query.filter(Blog.visible==visible)
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
            'visible': self.visible,
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