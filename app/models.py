import re
import boto3
import base64, os, jwt
from time import time
from app import db
from flask import jsonify
from geopy import distance
from datetime import datetime, timedelta
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.search import add_to_index, remove_from_index, query_index

class Query(BaseQuery, SearchQueryMixin):
    pass

class SearchMixin(object):
    @classmethod
    def search(cls, expression, page):
        ids, total = query_index(cls.__tablename__, expression, page, 37)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cdict(cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)))

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.configure_mappers()
db.event.listen(db.session, 'before_commit', SearchMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchMixin.after_commit)

def cdict(query, page=1, per_page=11):
        page = float(page)
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.dict() for item in resources.items],
            'pages': resources.pages,
            'total': resources.total}
        return data

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Nd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    tags = db.Column(db.JSON)

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'tags': self.tags
        }
        return data

    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    json = db.Column(db.JSON) 
    name = db.Column(db.Unicode)
    about = db.Column(db.Unicode)

    def dict(self):
        data = {
            'id': self.id,
            'json': self.json,
            'name': self.name,
            'about': self.about,
            'user': self.user.dict()
        }
        return data

    @staticmethod
    def exists(user, name):
        return Product.query.filter_by(user_id = user.id).count()>0

    def __init__(self, json, id, name):
        user = User.query.get(id)
        if exists(user, name):
            return None
        self.user = user
        self.name = name
        self.json = json
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def delete(id):
        db.session.delete(Item.query.get(id))

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

    def __init__(dict):
        for field in dict:
            if dict[field]:
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

saved_products = db.Table('saved_products',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('product', db.Integer, db.ForeignKey('product.id')))

saved_blogposts = db.Table('saved_blogposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('blogpost_id', db.Integer, db.ForeignKey('blogpost.id')))

saved_forumposts = db.Table('saved_forumposts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('forumpost_id', db.Integer, db.ForeignKey('forumpost.id')))

class User(db.Model):
    query_class = Query
    search_vector = db.Column(
        TSVectorType(
            'username', 'name', 'about', weights={'username': 'A', 'name': 'B', 'about': 'B'}))
    username = db.Column(db.Unicode)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))

    individual = db.Column(db.Boolean)

    id = db.Column(db.Integer, primary_key=True)
    custom = db.Column(db.JSON)
    tokens = db.relationship(Token, backref='user', lazy='dynamic')
    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    openby = db.Column(db.DateTime)
    closeby = db.Column(db.DateTime)

    online = db.Column(db.Boolean, default=False)
    sgn = db.Column(db.Integer)
    sgn_distance = db.Column(db.Float)

    items = db.relationship('Item', backref='user', lazy='dynamic')
    products = db.relationship('Product', backref='user', lazy='dynamic')
    
    saved_places = db.relationship('Place', secondary=saved_places, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_users = db.relationship('User', secondary=saved_users, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_items = db.relationship('Item', secondary=saved_items, backref='savers', lazy='dynamic')
    saved_products = db.relationship('Product', secondary=saved_products, backref='savers', lazy='dynamic')
    
    saved_forumposts = db.relationship('Forumpost', secondary=saved_forumposts, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_blogposts = db.relationship('Blogpost', secondary=saved_blogposts, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    cards = db.relationship(Card, secondary=cards, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    distance = db.Column(db.Unicode)
    logo_url = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)
    username = db.Column(db.Unicode(123), unique=True)

    visible = db.Column(db.Boolean, default=False)
    
    name = db.Column(db.Unicode(123))
    password_hash = db.Column(db.String(123))
    description = db.Column(db.Unicode(123))
    about = db.Column(db.UnicodeText())
    website = db.Column(db.String())
    phone = db.Column(db.String())
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show_email = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(373), index=True, unique=True)
    marketlnx = db.Column(db.Boolean, default=False)

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
            subject = (user.location['latitude'], user.location['longitude'])
            target = (target['latitude'], target['longitude'])
            user.distance = distance(subject, target)
        db.session.commit()
        return query.order_by(User.distance.desc())

    @staticmethod
    def distance(p1, p2):
        return distance.distance(p1, p2)

    def __init__(self, username, password):
        self.username=username
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
        return 'username: {}'.format(self.username)

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
            'name': self.name,
            'username': self.username,
            'token': self.token
        }
        if self.location != None:
            data['location'] = self.location
        return data

    def qdict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'username': self.username,
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
        self.username = data['username']
        self.name = data['name']
        self.about = data['about']
        self.phone = data['phone']
        self.website = data['website']
        self.location = data['location']
        if 'place_id' in data:
            self.place = Place.query.get(data['place_id'])
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

    def subscribed(self, year, module):
        return self.subscriptions.filter(
            subscriptions.c.subscription_id == s.id).count()>0