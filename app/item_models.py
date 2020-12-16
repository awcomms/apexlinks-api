from app import db
from flask import jsonify
from geopy import distance
from app.models import Field
from sqlalchemy_utils.types import TSVectorType
from app.models import Query, User, cdict

class Item(db.Model):
    query_class = Query
    search_vector = db.Column(
        TSVectorType(
            'name', 'about', weights={'name': 'A', 'about': 'B'}))
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    archived = db.Column(db.Boolean, default=False)
    itype = db.Column(db.Unicode)
    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    viewed = db.Column(db.JSON)
    price = db.Column(db.Unicode)
    fields = db.Column(db.JSON)
    json = db.Column(db.JSON)
    name = db.Column(db.Unicode)
    about = db.Column(db.Unicode)
    paid_in = db.Column(db.Unicode)

    @staticmethod
    def archive(id, token):
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        item = Item.query.get(id)
        if item.user != user:
            return {'errors': ['Item does not belong to user']}
        item.archived = True
        db.session.commit()

    @staticmethod
    def unarchive(id, token):
        errors = []
        user = User.query.filter_by(token=token).first()
        if not user:
            return {}, 401
        item = Item.query.get(id)
        if item.user != user:
            return {'errors': ['Item does not belong to user']}
        item.archived = False
        db.session.commit()
        return {}, 201

    @staticmethod
    def saved(user, item):
        return user.saved_items.filter(saved_items.c.item_id == item.id).count()>0

    @staticmethod
    def save(ids, token):
        user = User.query.filter_by(token=token).first()
        for id in ids:
            item = Item.query.get(id)
            if item.user != user:
                continue
            if not saved(user, item):
                user.saved_items.append(item)
        db.session.commit()
        return {}, 202

    @staticmethod
    def unsave(ids, token):
        user = User.query.filter_by(token=token).first()
        for id in ids:
            item = Item.query.get(id)
            if item.user != user:
                continue
            if saved(user, item):
                user.saved_items.remove(item)
        db.session.commit()
        return {}, 202

    @staticmethod
    def search(q, page, place_id=None, filters=None, position=None):
        items = Item.query.search('"' + q + '"', sort=True)
        if not is_instance(place_id, int):
            print('not')
            return cdict(items, page)
        items = items.filter_by(place_id=place_id)
        if position:
            items = location_sort(items, position)
        #if filters:
            #for f in filters:
                #items = items.filter(Item.fields[0][f['name']] == f['value'])
        return cdict(items, page)

    @staticmethod
    def location_sort(query, target):
        for item in query:
            subject = (item.location['latitude'], item.location['longitude'])
            target = (target['latitude'], target['longitude'])
            item.distance = distance(subject, target)
        db.session.commit()
        return query.order_by(Item.distance.desc())

    @staticmethod
    def distance(p1, p2):
        return distance.distance(p1, p2)

    def dict(self):
        data = {
            'id': self.id,
            'json': self.json,
            'name': self.name,
            'about': self.about,
            'user': self.user.dict(),
            'paid_in': self.paid_in
        }
        return data

    @staticmethod
    def exists(user, name):
        return Item.query.filter_by(user_id = user.id).count()>0

    def __init__(self, static_data):
        for field in static_data:
            setattr(self, field, static_data['field'])
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def edit(id, token, name, json):
        user = User.query.filter_by(token=token).first()
        item = Item.query.get(id)
        if item.user != user:
            return {}, 401
        item.name = name
        item.json = json
        db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def delete(ids, token):
        user = User.query.filter_by(token=token).first()
        item = Item.query.get(id)
        for id in ids:
            if item.user == user:
                db.session.delete(item)
        db.session.commit()
        return {}, 202
