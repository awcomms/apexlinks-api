import re
import boto3
import base64, os, jwt
from time import time
from app import db
from app.misc import dist
from flask import jsonify
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta
from flask import jsonify, current_app, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

saved_users = db.Table('saved_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

saved_items = db.Table('saved_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item', db.Integer, db.ForeignKey('item.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    save_count = db.Column(db.Integer)
    card = db.Column(db.JSON)
    score = db.Column(db.Integer)
    tags = db.Column(db.JSON)
    username = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    show_email = db.Column(db.Boolean, default=True)
    hide_location = db.Column(db.Boolean, default=False)

    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    openby = db.Column(db.DateTime)
    closedby = db.Column(db.DateTime)

    online = db.Column(db.Boolean, default=False)

    items = db.relationship('Item', backref='user', lazy='dynamic')
    
    saved_users = db.relationship('User', secondary=saved_users, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_items = db.relationship('Item', secondary=saved_items, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    
    images = db.Column(db.Unicode)
    image = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)

    subscribed = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=True)
    
    email = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode)
    password_hash = db.Column(db.String)
    about = db.Column(db.Unicode)
    website = db.Column(db.String)
    phone = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String, index=True, unique=True)

    @staticmethod
    def fuz(tags):
        query = User.query.filter(User.visible==True)
        for user in query:
            if type(user.tags) == list and tags:
                user.score = 0
                for tag in tags:
                        user.score += process.extractOne(tag, user.tags)
        db.session.commit()
        query = query.order_by(User.score.desc())
        print(query.all())
        return query

    def toggle_save(self, user):
        saved = self.user_saved(user.id)
        if not saved:
            self.saved_users.append(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()
        elif saved:
            self.saved_users.remove(user)
            db.session.commit()
            user.save_count = user.savers.count()
            db.session.commit()
        return self.user_saved(user.id)

    def item_saved(self, id):
        return self.saved_items.filter_by(id=id).count()>0

    def user_saved(self, id):
        return self.saved_users.filter_by(id==id).count()>0

    def place_saved(self, id):
        return self.saved_places.filter_by(place_id=id).count()>0

    @staticmethod
    def location_sort(query, target):
        for user in query:
            subject = (user.location['lat'], user.location['lon'])
            target = (target['lat'], target['lon'])
            user.distance = dist(subject, target)
        db.session.commit()
        return query.order_by(User.dist.desc())

    def __init__(self, username, password):
        self.set_password(password)
        self.username=username
        self.images=[]
        self.tags = []
        db.session.add(self)
        db.session.commit()
        
    def __repr__(self):
        return 'username: {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def dict(self):
        return {
            'id': self.id,
            'card': self.card,
            'image': self.image,
            'images': self.images,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'score': self.score,
            'token': self.token,
            'tags': self.tags,
            'location': self.location,
            'visible': self.visible,
            'subscribed': self.subscribed,
        }

    def edit(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])
        db.session.add(self)
        db.session.commit()