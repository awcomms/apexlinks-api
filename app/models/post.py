from sqlalchemy.orm import backref
from app import db

_replies = db.Table('_replies', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('reply_id', db.Integer, db.ForeignKey('reply.id')))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)
    image = db.relationship('Image', backref='post', lazy='dynamic')
    replies = db.relationship('Post', secondary=_replies, primaryjoin=id==_replies.c.post_id, secondary_join=id==_replies.c.reply_id, backref=db.backref('posts', lazy='dynamic', lazy='dynamic'))

    def __init__(self, text):
        self.text = text
        db.session.commit()

    # def TODO-M-M