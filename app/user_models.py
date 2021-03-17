from app import db
from fuzzywuzzy import process
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

xrooms = db.Table('xrooms',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    tags = db.Column(db.JSON)
    socket_id = db.Column(db.Unicode)
    username = db.Column(db.Unicode)
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    online = db.Column(db.Boolean, default=False)

    xrooms = db.relationship('Room', secondary=xrooms, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    
    visible = db.Column(db.Boolean, default=True)
    
    password_hash = db.Column(db.String)
    about = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String, index=True)

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

    def dict(self):
        return {
            'id': self.id,
            'socket_id': self.socket_id,
            'username': self.username,
            'score': self.score,
            'token': self.token,
            'tags': self.tags,
            'visible': self.visible,
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