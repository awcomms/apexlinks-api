import jwt
from time import time

from sqlalchemy.orm import backref
from app.misc.distance import distance
from app.models.junctions import xrooms
from app.vars.q import host, global_priority, default_user_fields
from app.misc.datetime_period import datetime_period
from app.misc.fields.score import field_score
import xml.etree.ElementTree as ET
from app.models.learn.result import Result

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app import db
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

_saved_users = db.Table('_saved_users',
                        db.Column('saver', db.Integer, db.ForeignKey('user.id')),
                        db.Column('savee', db.Integer, db.ForeignKey('user.id')))

_saved_items = db.Table('_saved_items',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                        db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
                        db.Column('tags', db.JSON))

search_attributes = [
    'username'
]

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
    settings = db.Column(db.JSON)
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

    distance = db.Column(db.Float)
    password_hash = db.Column(db.String)
    token = db.Column(db.String, index=True)
    score = db.Column(db.Float)
    hidden = db.Column(db.Boolean, default=False)
    socket_id = db.Column(db.Unicode)
    no_password = db.Column(db.Boolean)

    saved_users = db.relationship('User', secondary=_saved_users, primaryjoin=id == _saved_users.c.saver,
                                  secondaryjoin=id == _saved_users.c.savee, backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')

    def save_toggle_user(self, user):
        if self.user_saved(user):
            self.unsave_user(user)
        else:
            self.save_user(user)

    def user_saved(self, user):
        print(self, user)
        return self.saved_users.filter(
            _saved_users.c.savee == user.id
        ).count() > 0

    def save_user(self, user):
        if not self.user_saved(user):
            self.saved_users.append(user)
            db.session.commit()

    def unsave_user(self, user):
        if self.user_saved(user):
            self.saved_users.remove(user)
            db.session.commit()

    saved_items = db.relationship('Item', secondary=_saved_items, primaryjoin=(id == _saved_items.c.user_id),
                                  secondaryjoin=(id == _saved_items.c.item_id), backref=db.backref('savers', lazy='dynamic'), lazy='dynamic')
    
    def save_toggle_item(self, item):
        if self.item_saved(item):
            self.unsave_item(item)
        else:
            self.save_item(item)

    def item_saved(self, item):
        return self.saved_items.filter(
            _saved_items.c.item_id == item.id
        ).count() > 0

    def save_item(self, item):
        if not self.item_saved(item):
            self.saved_items.append(item)
            db.session.commit()

    def unsave_item(self, item):
        if self.item_saved(item):
            self.saved_items.remove(item)
            db.session.commit()

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
            differences.append((mod.datetime-previous_mod.datetime).seconds)
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
            return {'user': None, 'res': 'expired'}
        except BadSignature:
            print('BadSignature')
            return {'user': None, 'res': 'bad'}
        except Exception as e:
            print('static method really invalid token: ', e)
            return {'user': None, 'res': ''}
        if 'id' in data:
            u = User.query.get(data['id'])
            return {'user': u, 'res': ''}
        else:
            return {'user': None, 'res': ''}

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

    def __init__(self, username, password, email=None):
        fields = []
        for default_field in default_user_fields:
            value = ''
            if default_field == 'email':
                value = email
            fields.append({
                'label': default_field,
                'value': value
            })
        self.fields = fields
        self.email = email
        print('p', password)
        if not password:
            print('np')
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
        res = {
            'id': self.id,
            'score': self.score,
            'show_email': self.show_email,
            'hidden': self.hidden,
            'username': self.username,
            'name': self.name,
            'type': type(self).__name__.lower(),
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

        if 'user' in kwargs and kwargs['user'] and 'attrs' in kwargs:
            user = kwargs['user']
            # TODO
            for attr in kwargs['attrs']:
                if attr == 'saved':
                    res[attr] = user.user_saved(self)
                if hasattr(user, attr):
                    res[attr] = getattr(user, attr)
                else:
                    # TODO-error
                    pass

        if '_extra' in kwargs:
            res.update(kwargs['_extra'])
        
        return res

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()
        self.new_mod()
        db.session.commit()

from app.models.sitemap_index import SitemapIndex
from app.models.mod import Mod