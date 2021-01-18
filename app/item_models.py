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
    archived = db.Column(db.Boolean, default=False)
    img_urls = db.Column(db.JSON)
    itype = db.Column(db.Unicode)
    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    price = db.Column(db.Unicode)
    json = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    #description = db.Column(db.Unicode)
    paid_in = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(q, id, sort, archived, itype, tags, location, nation_id, state_id):
        query = Item.query\
        .join(User)\
        .filter(User.visible==True)
        if id:
            query.join(User, (User.id==id))
        if itype:
            query.filter(Item.itype==itype)
        if archived:
            query.filter(Item.archived==True)
        else:
            query.filter(Item.archived==False)
        if nation_id:
            query.join(User, (User.nation_id==nation_id))
        if state_id:
            query.join(User, (User.state_id==state_id))
        
        for item in query:
            if item.tags:
                for tag in item.tags:
                    if process.extractOne(tag, tags)[1] < 90:
                        query.filter(Item.id != item.id)
        if q != '':
            for item in query:
                ratio = fuzz.ratio(q, item.name)
                #description_ratio = fuzz.token_set_ratio(q, item.description)
                #if ratio < 79 or description_ratio < 90: 
                    query.filter(Item.id != item.id)
                if ratio < 79: 
                else:
                    item.score = ratio
            if sort == 'relevance':
                query.order_by(Item.score.desc())
        if sort == 'save_count':
            query.order_by(Item.savers.count().desc())
        if location and sort == 'location':
            query = Item.location_sort(query, location)
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
            item.distance = dist(subject, target)
        db.session.commit()
        return query.order_by(Item.distance.desc())

    def dict(self):
        data = {
            'id': self.id,
            'link': self.link,
            'name': self.name,
            #'description': self.description,
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
        return jsonify(self.dict())