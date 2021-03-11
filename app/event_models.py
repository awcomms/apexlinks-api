from app import db
from flask import jsonify
from fuzzywuzzy import process, fuzz
from app.models import User
from app.misc import dist

class Event(db.Model):
    tags = db.Column(db.JSON)
    save_count = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visible = db.Column(db.Boolean, default=True)
    image = db.Column(db.Unicode)
    images = db.Column(db.JSON)
    itype = db.Column(db.Unicode)
    price = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(id, visible, itype, tags):
        query = Event.query.join(User)\
        .filter(User.visible==True)
        if id:
            query=query.filter(User.id==id)
        if itype:
            query=query.filter(Event.itype==itype)
        try:
            query=query.filter(Event.visible==visible)
        except:
            pass
        for event in query:
            event.score = 0
            for tag in tags:
                try:
                    event.score += process.extractOne(tag, event.tags)[1]
                except:
                    pass
        db.session.commit()
        query.order_by(Event.score.desc())
        return query

    def toggle_save(self, user):
        saved = user.event_saved(self.id)
        print(saved)
        if not saved:
            user.saved_events.append(self)
            db.session.commit()
            self.save_count = self.savers.count()
            db.session.commit()
        elif saved:
            user.saved_events.remove(self)
            db.session.commit()
            self.save_count = self.savers.count()
            db.session.commit()
        print(user.event_saved(self.id))
        return user.event_saved(self.id)

    @staticmethod
    def is_visible(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        event = Event.query.get(id)
        if event.user != user:
            return {'errors': ['Event does not belong to user']}
        event.visible = True
        db.session.commit()

    @staticmethod
    def unvisible(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        event = Event.query.get(id)
        if event.user != user:
            return {'errors': ['Event does not belong to user']}
        event.visible = False
        db.session.commit()
        return {}, 201

    @staticmethod
    def location_sort(query, target):
        for event in query:
            subject = (event.location['lat'], event.location['lon'])
            target = (target['lat'], target['lon'])
            event.distance = dist(subject, target)
        db.session.commit()
        return query.order_by(Event.distance.desc())

    def dict(self):
       return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'itype': self.itype,
            'description': self.description,
            'image': self.image,
            'images': self.images,
            'price': self.price,
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