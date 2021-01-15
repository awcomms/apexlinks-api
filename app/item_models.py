from app import db
from flask import jsonify
from geopy import distance
from fuzzywuzzy import process, fuzz
from app.models import User, cdict

class Item(db.Model):
    save_count = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    archived = db.Column(db.Boolean, default=False)
    img_urls = db.Column(db.JSON)
    itype = db.Column(db.Unicode)
    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    price = db.Column(db.Unicode)
    json = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    description = db.Column(db.Unicode)
    paid_in = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(q, id, itype, tags, position, nation_id, state_id):
        query = Item.query\
        .join(User)\
        .filter(User.visible==True)\
        .filter(Item.itype==itype)\
        .filter(Item.archived==False)
        if id:
            query.join(User, (User.id==id))
        if nation_id:
            query.join(User, (User.nation_id==nation_id))
        if state_id:
            query.join(User, (User.state_id==state_id))
        
        for item in query:
            for tag in item.tags:
                if process.extractOne(tag, tags)[1] < 90:
                    query.filter(Item.id != item.id)
        if q != '':
            for item in query:
                ratio = fuzz.ratio(q, item.name)
                description_ratio = fuzz.token_set_ratio(q, item.description)
                if ratio < 79 or description_ratio < 90: 
                    query.filter(Item.id != item.id)
                else:
                    item.score = ratio
            if sort == 'relevance':
                query.order_by(Item.score.desc())
        if sort == 'save_count':
            query.order_by(Item.savers.count().desc())
        if sort == 'position':
            query = location_sort(query, position)
        return query

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
    def location_sort(query, target):
        for item in query:
            subject = (item.location['lat'], item.location['lng'])
            target = (target['lat'], target['lng'])
            item.distance = distance(subject, target)
        db.session.commit()
        return query.order_by(Item.distance.desc())

    def sgn_sort(query, sgn):
        for item in query:
            item.sgn_distance = item.sgn - sgn
        db.session.commit
        return query.order_by(Item.sgn_distance.desc())

    @staticmethod
    def distance(p1, p2):
        return distance.distance(p1, p2)

    def dict(self):
        data = {
            'id': self.id,
            'link': self.link,
            'name': self.name,
            'description': self.description,
            'img_urls': self.img_urls,
            'user': {
                'id': self.user.id,
            },
            'paid_in': self.paid_in
        }
        if self.user.show_email:
            data['user']['email'] = self.user.email
        if not self.user.hide_location:
            data['user']['location'] = self.user.location
        return data

    @staticmethod
    def exists(user, name):
        return Item.query.filter_by(user_id = user.id).count()>0

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