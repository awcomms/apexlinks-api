from sqlalchemy.orm import backref
from app import db
from fuzzywuzzy import process
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

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
    address = db.Column(db.Unicode)
    tags = db.Column(db.JSON)

    password_hash = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String, index=True)
    score = db.Column(db.Integer)
    visible = db.Column(db.Boolean, default=True)
    socket_id = db.Column(db.Unicode)

    xrooms = db.relationship('Room', secondary=xrooms, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    items = db.relationship('Item', backref='user', lazy='dynamic')
    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    subs = db.relationship('Sub', backref='user', lazy='dynamic')

    @staticmethod
    def fuz(tags):
        query = User.query.filter(User.visible==True)
        for user in query:
            if isinstance(user.tags, list) and tags:
                user.score = 0
                for tag in tags:
                    try:
                        user.score += process.extractOne(tag, user.tags)[1]
                    except:
                        pass
        db.session.commit()
        query = query.order_by(User.score.desc())
        return query

    def __init__(self, username, password):
        self.set_password(password)
        self.username=username
        self.unseen_rooms=[]
        self.in_rooms=[]
        self.tags=[username]
        db.session.add(self)
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

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def dict(self, **kwargs):
        return {
            'id': self.id,
            'socket_id': self.socket_id,
            'score': self.score,
            'token': self.token,
            'visible': self.visible,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'about': self.about,
            'address': self.address,
            'tags': self.tags
        }

    def edit(self, data):
        print(data)
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])
        db.session.commit()