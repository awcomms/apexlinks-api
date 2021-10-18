import jwt
from time import time
from app.vars import host
from app.models.mod import Mod
from app.models.sitemap_index import SitemapIndex

from itsdangerous import (TimedJSONWebSignatureSerializer
                            as Serializer, BadSignature, SignatureExpired)
from app.misc.fields.clean import clean

from app import db
from flask import current_app
from fuzzywuzzy import fuzz, process
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
    location = db.Column(db.JSON)
    fields = db.Column(db.JSON)
    address = db.Column(db.JSON)
    tags = db.Column(db.JSON)
    card = db.Column(db.JSON)
    # folders = db.relationship('Folder', backref='user', lazy='dynamic')
    image = db.Column(db.Unicode)
    last_paid = db.Column(db.DateTime)
    paid = db.Column(db.Boolean, default=False)

    mods = db.relationship('Mod', backref='user', lazy='dynamic')

    show_email = db.Column(db.Boolean, default=True)

    password_hash = db.Column(db.String)
    token = db.Column(db.String, index=True)
    score = db.Column(db.Integer)
    hidden = db.Column(db.Boolean, default=False)
    socket_id = db.Column(db.Unicode)
    no_password = db.Column(db.Boolean)

    items = db.relationship('Item', backref='user', lazy='dynamic')
    xrooms = db.relationship('Room', secondary=xrooms, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    subs = db.relationship('Sub', backref='user', lazy='dynamic')

    def last_mod(self):
        # returns most recent of self.mods
        return self.mods.order_by(Mod.date.desc()).first()

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def changefreq():
        # method to calculate recent change frequency based on past change frequency methods
        return 'always' or 'hourly' or 'daily' or 'weekly' or 'monthly' or 'yearly' or 'never'

    def url(self):
        return f'{host}/{self.username}'

    @staticmethod
    def activate(id):
        user = User.query.get(id)
        user.paid = True
        db.session.commit()

    def get_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = 31536000)
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
    def get(tags):
        query = User.query.filter(User.hidden==False)
        # query = query.filter(User.paid==True)
        fields = []
        for tag in tags:
            try:
                fieldList = tag.split(':')
                field = {
                    'label': fieldList[0],
                    'value': fieldList[1]
                }
                fields.append(field)
                tags.remove(tag)
                continue
            except:
                pass
        for idx, field in enumerate(fields):
            res = clean(field)
            if isinstance(res, str):
                print('clean field error: ', res)
                continue
                # return {'error': res}
            fields[idx] = res
        for user in query:
            user.score = 0
            if isinstance(user.tags, list) and tags:
                for tag in tags:
                    try:
                        user.score += process.extractOne(tag, user.tags + user.attr_tags())[1]
                    except:
                        pass
            for field in fields:
                max = 0
                for user_field in user.fields:
                    label_score = fuzz.ratio(field['label'], user_field['label'])
                    value_score = fuzz.ratio(field['value'], user_field['value'])
                    score = label_score + value_score
                    if score > max:
                        max = score
                user.score += max
        db.session.commit()
        query = query.order_by(User.score.desc())
        return query

    def attr_tags(self):
        res = []
        for attr in search_attributes:
            res.append(self.attr)

    def __init__(self, username, password, email=None):
        self.email=email
        if not password:
            self.no_password = True
        self.set_password(password)
        self.username=username
        db.session.add(self)
        db.session.commit()
        SitemapIndex.add_user(self)
        db.session.commit()
    
    def __repr__(self):
        return 'username: {}'.format(self.username)

    def in_room(self, room):
        return self.xrooms.filter_by(id=room.id).count()>0

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
        print('self.fields: ', self.fields)
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