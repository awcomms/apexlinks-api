import re
import boto3
import base64, os, jwt
from time import time
from app import db
from flask import jsonify
from geopy import distance
from datetime import datetime, timedelta
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

def cdict(query, page=1, per_page=10):
        page = float(page)
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.dict() for item in resources.items],
            'pages': resources.pages,
            'total': resources.total}
        return data

saved_places = db.Table('saved_places',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('place_id', db.Integer, db.ForeignKey('place.id')))

saved_users = db.Table('saved_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

saved_items = db.Table('saved_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item', db.Integer, db.ForeignKey('item.id')))

class User(db.Model):
    save_count = db.Column(db.Integer)
    card = db.Column(db.JSON)
    score = db.Column(db.Integer)
    tags = db.Column(db.JSON)
    username = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    show_email = db.Column(db.Boolean, default=True)
    hide_location = db.Column(db.Boolean, default=False)

    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    openby = db.Column(db.DateTime)
    closedby = db.Column(db.DateTime)

    online = db.Column(db.Boolean, default=False)

    items = db.relationship('Item', backref='user', lazy='dynamic')
    
    saved_places = db.relationship('Place', secondary=saved_places, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_users = db.relationship('User', secondary=saved_users, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_items = db.relationship('Item', secondary=saved_items, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    
    distance = db.Column(db.Unicode)
    logo_url = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)

    subscribed = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=False)
    
    email = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode)
    password_hash = db.Column(db.String)
    about = db.Column(db.Unicode)
    website = db.Column(db.String)
    phone = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(373), index=True, unique=True)

    @staticmethod
    def fuz(q, sort, tags, position, nation_id, state_id):
        query = User.query\
        .filter(User.subscribed==True)\
        .filter(User.visible==True)
        if nation_id:
            query.filter(User.nation_id==nation_id)
        if state_id:
            query.filter(User.state_id==state_id)
        
        for user in query:
            for tag in user.tags:
                if process.extractOne(tag, tags)[1] < 90:
                    query.filter(User.id != user.id)
        if q != '':
            for user in query:
                ratio = fuzz.ratio(q, user.name)
                about_ratio = fuzz.token_set_ratio(q, user.about)
                if ratio < 79 or about_ratio < 90: 
                    query.filter(User.id != user.id)
                else:
                    user.score = ratio
            if sort == 'relevance':
                query.order_by(User.score.desc())
        if sort == 'save_count':
            query.order_by(User.save_count.desc())
        if sort == 'position':
            query = location_sort(query, position)
        return query

    def toggle_item_save(self, id):
        item = Item.query.get(id)
        if not self.item_saved(id):
            self.saved_items.append(item)
            db.session.commit()
            item.save_count = item.savers.count()
            db.session.commit()
        elif self.item.saved(id):
            self.saved_items.remove(item)
            db.session.commit()
            item.save_count = item.savers.count()
            db.session.commit()

    def toggle_user_save(self, id):
        user = Item.query.get(id)
        if not self.user_saved(id):
            self.saved_users.append(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()
        elif self.user.saved(id):
            self.saved_users.remove(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()

    def item_saved(self, id):
        return self.saved_items.filter_by(id=id).count()>0

    def save_item(self, id):
        if not self.item_saved(id):
            item = Item.query.get(id)
            self.saved_items.append(item)
            db.session.commit()
            item.save_count = item.savers.count()
            db.session.commit()

    def unsave_item(self, id):
        if self.item_saved(id):
            item = Item.query.get(id)
            self.saved_items.remove(item)
            db.session.commit()
            item.save_count = item.savers.count()
            db.session.commit()

    def user_saved(self, id):
        return self.saved_users.filter_by(id==id).count()>0

    def save_user(self, id):
        if not self.user_saved(id):
            user = User.query.get(id)
            self.saved_users.append(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()

    def unsave_user(self, id):
        if self.user_saved(id):
            user = User.query.get(id)
            self.saved_users.remove(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()

    def place_saved(self, id):
        return self.saved_places.filter_by(place_id=id).count()>0

    def save_place(self, place):
        if not self.place_saved(place.id):
            self.saved_places.append(place)
            db.session.commit()
            place.save_count = place.savers.count()
            db.session.commit()

    def unsave_place(self, place):
        if self.place_saved(place.id):
            self.saved_places.remove(place)
            db.session.commit()
            place.save_count = place.savers.count()
            db.session.commit()

    @staticmethod
    def location_sort(query, target):
        for user in query:
            subject = (user.location['lat'], user.location['lng'])
            target = (target['lat'], target['lng'])
            user.distance = distance(subject, target)
        db.session.commit()
        return query.order_by(User.distance.desc())

    @staticmethod
    def distance(p1, p2):
        return distance.distance(p1, p2)

    def __init__(self, username, email, password):
        self.username=username
        self.email=email
        self.set_password(password)
        db.session.add(self)
        db.session.commit()
        
    def __repr__(self):
        return 'email: {}'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def dict(self):
        data = {
            'id': self.id,
            'card': self.card,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'token': self.token,
            'tags': self.tags,
            'location': self.location,
            'visible': self.visible,
            'subscribed': self.subscribed,
        }
        if self.location != None:
            data['location'] = self.location
        return data

    def edit(self, data):
        print(data)
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])
        print(self.phone)
        db.session.add(self)
        db.session.commit()