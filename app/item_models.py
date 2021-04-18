from app import db
from flask import jsonify
from fuzzywuzzy import process, fuzz
from app.user_model import User

class Item(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visible = db.Column(db.Boolean, default=True)
    image = db.Column(db.Unicode)
    data = db.Column(db.Unicode)
    images = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    redirect = db.Column(db.Boolean, default=True)
    itype = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    itext = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(id, visible, tags):
        query = Item.query.join(User)
        if not id:
            query = query.filter(User.visible==True)
        elif id:
            query = query.filter(User.id==id)
        try:
            query = query.filter(Item.visible==visible)
        except:
            pass
        for item in query:
            item.score = 0
            for tag in tags:
                try:
                    item.score += process.extractOne(tag, item.tags)[1]
                except:
                    pass
        db.session.commit()
        query = query.order_by(Item.score.desc())
        return query

    def dict(self, **kwargs):
       return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'itype': self.itype,
            'itext': self.itext,
            'image': self.image,
            'images': self.images,
            'visible': self.visible,
            'redirect': self.redirect,
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
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()