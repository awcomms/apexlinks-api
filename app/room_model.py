from app import db
from fuzzywuzzy import process
from app.user_model import User, xrooms

class Room(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    open = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    messages = db.relationship('Message', backref='room', lazy='dynamic')
    name = db.Column(db.Unicode)
    unseen = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float)

    def xfuz(id, tags):
        query = Room.query
        if not id:
            query = query.filter(Room.open==True)
        else:
            query=query.join(xrooms).filter(xrooms.c.user_id == id)
        for room in query:
            room.score = 0
            for tag in tags:
                try:
                    room.score += process.extractOne(tag, room.tags)[1]
                except:
                    pass
        db.session.commit()
        query=query.order_by(Room.score.desc())
        return query

    @staticmethod
    def fuz(id, tags):
        query = Room.query.join(User)
        if not id:
            query=query.filter(Room.open==True)
        else:
            query=query.filter(User.id==id)
        for room in query:
            room.score = 0
            for tag in tags:
                try:
                    room.score += process.extractOne(tag, room.tags)[1]
                except:
                    pass
        db.session.commit()
        query=query.order_by(Room.score.desc())
        return query

    def dict(self, **kwargs):
        uid = None
        seen = None
        if kwargs['user']:
            uid = kwargs['user'].id
        row = db.engine.execute(xrooms.select().where(xrooms.c.user_id==uid)\
            .where(xrooms.c.room_id==self.id)).first()
        if row:
            seen = row['seen']
        data = {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'open': self.open,
            'user': self.user.username
        }
        if seen is False:
            data['unseen'] = True
        if not self.open:
            data['users'] = [user.username for user in self.users]
        return data

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