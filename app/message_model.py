from datetime import datetime
from app import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    value = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, value, user, room):
        self.value=value
        self.user=user
        self.room=room
        db.session.add(self)
        db.session.commit()

    def dict(self, **kwargs):
        return {
            'user': self.user.username,
            'room': self.room.id,
            'value': self.value
        }