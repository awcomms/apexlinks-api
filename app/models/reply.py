# from sqlalchemy.orm import backref
# from app import db
# from app.relationship_tables import reply_images

# _replies = db.Table('_replies', 
#     db.Column('reply_id', db.Integer, db.ForeignKey('reply.id')),
#     db.Column('reply_id', db.Integer, db.ForeignKey('reply.id')))

# class Reply(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.Unicode)
#     image = db.relationship('Image', secondary=reply_images, backref=db.backref('replies', lazy='dynamic'), lazy='dynamic')
#     replies = db.relationship('Reply', secondary=_replies, primaryjoin=id==_replies.c.reply_id, secondaryjoin=id==_replies.c.reply_id, backref=db.backref('replies', lazy='dynamic'))

#     def __init__(self, text):
#         self.text = text
#         db.session.commit()

#     # def TODO-M-M