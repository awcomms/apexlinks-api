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
    visible = db.Column(db.Boolean, default=False)
    image = db.Column(db.Unicode)
    images = db.Column(db.JSON)
    itype = db.Column(db.Unicode)
    price = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(id, visible, itype, tags):
        query_length = len(tags)
        query = Item.query.join(User)\
        .filter(User.visible==True)
        if id:
            query.filter(User.id==id)
        if itype:
            query.filter(Item.itype==itype)
        if visible:
            query.filter(Item.visible==True)
        else:
            query.filter(Item.visible==False)
        for item in query:
            length = len(item.tags)
            item.score = 1
            if tags and item.tags:
                for tag in item.tags:
                    ratio = query_length/length
                    item.score += ratio*process.extractOne(tag, tags)[1]
        query.order_by(Item.score.desc())
        return query

    def toggle_save(self, user):
        saved = user.item_saved(self.id)
        print(saved)
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
        print(user.item_saved(self.id))
        return user.item_saved(self.id)

    @staticmethod
    def visible(id, token):
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
        data = {
            'id': self.id,
            'link': self.link,
            'name': self.name,
            'itype': self.itype,
            'username': self.user.username,
            'description': self.description,
            'image': self.image,
            'images': self.images,
            'price': self.price,
            'visible': self.visible
        }
        if self.user.show_email:
            data['user']['email'] = self.user.email
        if not self.user.hide_location:
            data['user']['location'] = self.user.location
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