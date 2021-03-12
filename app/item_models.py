from app import db
from flask import jsonify
from fuzzywuzzy import process, fuzz
from app.models import User
from app.misc import dist

class Item(db.Model):
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
        query = Item.query.join(User)\
        .filter(User.visible==True)
        if id:
            query=query.filter(User.id==id)
        if itype:
            query=query.filter(Item.itype==itype)
        try:
            query=query.filter(Item.visible==visible)
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
        query.order_by(Item.score.desc())
        return query

    def toggle_save(self, user):
        saved = user.item_saved(self.id)
        if not saved:
            user.saved_items.append(self)
            db.session.commit()
            self.save_count = self.savers.count()
            db.session.commit()
        elif saved:
            user.saved_items.remove(self)
            db.session.commit()
            self.save_count = self.savers.count()
            db.session.commit()
        return user.item_saved(self.id)

    @staticmethod
    def is_visible(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        item = Item.query.get(id)
        if item.user != user:
            return {'errors': ['Item does not belong to user']}
        item.visible = True
        db.session.commit()

    @staticmethod
    def unvisible(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        item = Item.query.get(id)
        if item.user != user:
            return {'errors': ['Item does not belong to user']}
        item.visible = False
        db.session.commit()
        return {}, 201

    @staticmethod
    def location_sort(query, target):
        for item in query:
            subject = (item.location['lat'], item.location['lon'])
            target = (target['lat'], target['lon'])
            item.distance = dist(subject, target)
        db.session.commit()
        return query.order_by(Item.distance.desc())

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