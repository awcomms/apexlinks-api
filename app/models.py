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

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorization_code = db.Column(db.Unicode)
    bin = db.Column(db.Unicode)
    last4 = db.Column(db.Unicode)
    exp_month = db.Column(db.Unicode)
    exp_year = db.Column(db.Unicode)
    card_type = db.Column(db.Unicode)
    bank = db.Column(db.Unicode)
    country_code = db.Column(db.Unicode)
    brand = db.Column(db.Unicode)
    account_name = db.Column(db.Unicode)
    signature = db.Column(db.Unicode)
    reusable = db.Column(db.Boolean)

    def __init__(data):
        for field in data:
            if data[field]:
                setattr(self, field, data[field])
        db.session.commit()

    def dict(self):
        data = {
            'user_id': self.user_id,
            'authorizatiion_code': self.authorization_code,
            'card_type': self.card_type,
            'signature': self.signature,
            'last4': self.last4,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'bin': self.bin,
            'bank': self.bank,
            'signature': self.signature,
            'reusable': self.reusable,
            'nation_code': self.nation_code,
        }
        return data

    def from_dict(self, data):
        for field in ['authorization_code', 'card_type', 'last4', 'exp_month', 'exp_year', 'bin', 'bank', 'signature', 'reusable', 'nation_code']:
            setattr(self, field, data[field])

cards = db.Table('cards',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')))

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
    saved_items = db.relationship('Item', secondary=saved_items, backref='savers', lazy='dynamic')
    
    cards = db.relationship(Card, secondary=cards, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    distance = db.Column(db.Unicode)
    logo_url = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)

    subscribed = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=False)
    
    email = db.Column(db.Unicode(123), unique=True)
    name = db.Column(db.Unicode(123))
    password_hash = db.Column(db.String(123))
    description = db.Column(db.Unicode(123))
    about = db.Column(db.UnicodeText())
    website = db.Column(db.String())
    phone = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(373), index=True, unique=True)

    @staticmethod
    def fuz(tags, q, position, nation_id, state_id):
        query = User.query\
        .filter(User.subscribed==True)\
        .filter(User.visible==True)\
        if nation_id:
            query.filter(User.nation_id==nation_id)
        if state_id:
            query.filter(User.state_id==state_id))
        
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
            query.order_by(User.score.desc())
        if position:
            query = location_sort(query, position)
        return query

    def place_saved(self, id):
        return self.saved_places.filter_by(place_id=id).count()>0

    def save_place(self, place):
        if not self.place_saved(place.id):
            self.saved_places.append(place)
        db.session.commit()

    def unsave_place(self, place):
        if self.place_saved(place.id):
            self.saved_places.remove(place)
        db.session.commit()

    @staticmethod
    def search(q, page, position):
        users = User.query.search('"' + q + '"', sort=True)
        print(users)
        if position:
            print('position')
            users = location_sort(users, position)
        return cdict(users, page)

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

    def __init__(self, email, password):
        self.email=email
        self.set_password(password)
        db.session.add(self)
        db.session.commit()

    def get_utoken(self, expires_in=600):
        return jwt.encode(
            {'confirm_account': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def check_utoken(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['confirm_account']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return 'email: {}'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def add_item(id, name):
        user = User.query.get(id)
        Item(user, name)

    def dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'token': self.token,
            'tags': self.tags,
            'location': self.location,
            'visible': self.visible,
            'cards': [card.dict() for card in self.cards],
            'subscribed': self.subscribed,
        }
        if self.location != None:
            data['location'] = self.location
        return data

    def qdict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'about': self.about,
            'website': self.website,
            'token': self.token,
            'saved_users': cdict(self.saved_users),
            'saved_items': cdict(self.saved_items),
            'items': cdict(self.items),
            'products': cdict(self.products)
        }
        if self.location != None:
            data['location'] = self.location
        return data

    def from_dict(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data['field'])
        if 'password' in data:
            self.set_password(data['password'])
        db.session.add(self)
        db.session.commit()

    def add_card(self, card):
        if not self.has_card(card):
            self.cards.append(card)

    def remove_card(self, card):
        if self.has_card(card):
            self.remove(card)

    def has_card(self, card):
        return self.cards.filter(
            cards.c.card_id == card.id).count() > 0

    def subscribe(self, year, module):
        s=Subscription(year, module)
        self.subscriptions.append(s)
        db.session.commit()

    def unsubscribe(self, year, module):
        s=Subscription(year, module)
        self.subscriptions.remove(s)
        db.session.commit()