import jwt
from time import time
from app.vars.q import host, global_priority, default_user_fields
from app.misc.datetime_period import datetime_period
from app.misc.fields.score import field_score
import xml.etree.ElementTree as ET
from app.models.learn.result import Result

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app import db
from flask import current_app
from fuzzywuzzy import process
from werkzeug.security import check_password_hash, generate_password_hash

search_attributes = [
    'username'
]

xrooms = db.Table('xrooms',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
                  db.Column('seen', db.Boolean))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    phone = db.Column(db.Unicode)
    website = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    about = db.Column(db.Unicode)
    market_id = db.Column(db.Integer, db.ForeignKey('market.id'))
    location = db.Column(db.JSON)
    fields = db.Column(db.JSON)
    address = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    card = db.Column(db.JSON)
    # folders = db.relationship('Folder', backref='user', lazy='dynamic')
    image = db.Column(db.Unicode)
    last_paid = db.Column(db.DateTime)
    paid = db.Column(db.Boolean, default=False)

    notes = db.relationship('Note', backref='author', lazy='dynamic')
    show_email = db.Column(db.Boolean, default=True)
    author = db.Column(db.JSON, default={})

    mods = db.relationship('Mod', backref='user', lazy='dynamic')
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))

    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    results = db.relationship(Result, backref='user', lazy='dynamic')

    password_hash = db.Column(db.String)
    token = db.Column(db.String, index=True)
    score = db.Column(db.Integer)
    hidden = db.Column(db.Boolean, default=False)
    socket_id = db.Column(db.Unicode)
    no_password = db.Column(db.Boolean)

    items = db.relationship('Item', backref='user', lazy='dynamic')
    xrooms = db.relationship('Room', secondary=xrooms, backref=db.backref(
        'users', lazy='dynamic'), lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    subs = db.relationship('Sub', backref='user', lazy='dynamic')

    def xml(self):
        entry = ET.Element('url')

        loc = ET.Element('loc')
        loc.text = self.url()
        entry.append(loc)

        lastmod = ET.Element('lastmod')
        lastmod_date = self.lastmod
        lastmod_str = str(lastmod_date)
        lastmod.text = lastmod_str
        entry.append(lastmod)

        changefreq = ET.Element('changefreq')
        changefreq.text = self.changefreq()
        entry.append(changefreq)

        priority = ET.Element('priority')
        priority.text = global_priority
        entry.append(priority)

        return entry
    
    def last_modification(self):
        return self.mods.order_by(Mod.datetime.desc()).first()

    def lastmod(self):
        str(self.last_modification())

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def changefreq(self):
        differences = []
        query = self.mods.order_by(Mod.datetime.asc())
        previous_mod = None
        for mod in query:
            if not previous_mod:
                previous_mod = mod
                continue
            differences.append(mod-previous_mod.total_seconds())
            previous_mod = mod
        if len(differences):
            average = sum(differences) / len(differences)
            period = datetime_period(average)
            print('dp', period)
            return period
        else:
            return 'always'

    def url(self):
        return f'{host}/{self.username}'

    @staticmethod
    def activate(id):
        user = User.query.get(id)
        user.paid = True
        db.session.commit()

    def get_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=31536000)
        token = s.dumps({'id': self.id}).decode('utf-8')
        return token

    @staticmethod
    def check_token(token):
        print('serializer got: ', token)
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            print('SignatureExpired')
            return 'expired'
        except BadSignature:
            print('BadSignature')
            return 'bad'
        except Exception as e:
            print('sle: ', e)
            return None
        id = data['id']
        u = User.query.get(id)
        return u

    def set_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def check_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def get(tags, fields):
        tag_fields = [
            'name'
        ]
        tags_from_fields = []
        query = User.query
        for user in query:
            if user.fields:
                for field in user.fields:
                    if field['label'] in tag_fields:
                        tags_from_fields.append(field['value'])
            user.score = 0
            if isinstance(user.tags, list) and tags:
                for tag in tags:
                    try:
                        user.score += process.extractOne(
                            tag, user.tags)[1]
                    except:
                        pass
            # if fields and user.fields:
            #     user.score += field_score(user.fields, fields)
        db.session.commit()
        query = query.order_by(User.score.desc())
        return query

    def __init__(self, username, password, email=None):
        fields = []
        for default_field in default_user_fields:
            fields.append({
                'label': default_field,
                'value': ''
            })
        self.fields = fields
        self.email = email
        if not password:
            self.no_password = True
        else:
            self.set_password(password)
        self.username = username
        db.session.add(self)
        db.session.commit()
        self.new_mod()
        SitemapIndex.add_user(self)

    def __repr__(self):
        return 'username: {}'.format(self.username)

    def in_room(self, room):
        return self.xrooms.filter_by(id=room.id).count() > 0

    def join(self, room):
        if not self.in_room(room):
            self.xrooms.append(room)
            db.session.commit()

    def leave(self, room):
        if self.in_room(room):
            self.xrooms.remove(room)
            db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def dict(self, **kwargs):
        return {
            'id': self.id,
            'score': self.score,
            'show_email': self.show_email,
            'hidden': self.hidden,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'paid': self.paid,
            'fields': self.fields,
            'phone': self.phone,
            'image': self.image,
            'author': self.author,
            'website': self.website,
            'about': self.about,
            'address': self.address,
            'tags': self.tags,
        }

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()
        self.new_mod()
        db.session.commit()

from app.models.sitemap_index import SitemapIndex
from app.models.mod import Mod