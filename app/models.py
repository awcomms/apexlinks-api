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

saved_groups = db.Table('saved_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group', db.Integer, db.ForeignKey('group.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    save_count = db.Column(db.Integer)
    card = db.Column(db.JSON)
    score = db.Column(db.Integer)
    tags = db.Column(db.JSON)
    username = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    show_email = db.Column(db.Boolean, default=True)

    location = db.Column(db.JSON)
    distance = db.Column(db.Float)
    openby = db.Column(db.DateTime)
    closedby = db.Column(db.DateTime)

    online = db.Column(db.Boolean, default=False)

    groups = db.relationship('Group', backref='user', lazy='dynamic')
    
    saved_users = db.relationship('User', secondary=saved_users, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    saved_groups = db.relationship('Group', secondary=saved_groups, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    
    images = db.Column(db.JSON)
    image = db.Column(db.Unicode)
    customer_code = db.Column(db.Unicode)

    subscribed = db.Column(db.Boolean, default=False)
    visible = db.Column(db.Boolean, default=True)
    
    email = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    password_hash = db.Column(db.String)
    about = db.Column(db.Unicode)
    website = db.Column(db.String)
    phone = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String, index=True)

    @staticmethod
    def fuz(tags):
        query = User.query.filter(User.visible==True)
        for user in query:
            if type(user.tags) == list and tags:
                user.score = 0
                for tag in tags:
                    try:
                        user.score += process.extractOne(tag, user.tags)[1]
                    except:
                        pass
        db.session.commit()
        query = query.order_by(User.score.desc())
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

    def group_saved(self, id):
        return self.saved_groups.filter_by(id=id).count()>0

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
        self.tags=[]
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
            'image': self.image,
            'images': self.images,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'score': self.score,
            'token': self.token,
            'tags': self.tags,
            'visible': self.visible,
            'subscribed': self.subscribed,
        }

    def edit(self, data):
        setattr(self, 'visible', data['visible'])
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])
        db.session.add(self)
        db.session.commit()