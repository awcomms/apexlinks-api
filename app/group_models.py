from app import db
from flask import jsonify
from fuzzywuzzy import process, fuzz
from app.models import User

class Group(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    socket_id = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visible = db.Column(db.Boolean, default=True)
    users = db.Column(db.JSON)
    name = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(id, visible, tags):
        query = Group.query.join(User)
        if id:
            query=query.filter(User.id==id)
        try:
            query=query.filter(Group.visible==visible)
        except:
            pass
        for group in query:
            group.score = 0
            for tag in tags:
                try:
                    group.score += process.extractOne(tag, group.tags)[1]
                except:
                    pass
        db.session.commit()
        query=query.order_by(Group.score.desc())
        return query

    def dict(self):
       return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
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