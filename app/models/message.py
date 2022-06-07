from datetime import datetime, timezone

from sqlalchemy.orm import backref
from app import db

message_replies = db.Table("message_replies",
    db.Column('message', db.Integer, db.ForeignKey('message.id')),
    db.Column('reply', db.Integer, db.ForeignKey('message.id')))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    value = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    replies = db.relationship(
        'Message',
        secondary=message_replies,
        primaryjoin=id==message_replies.c.message,
        secondaryjoin=id==message_replies.c.reply,
        backref='messages')

    def __init__(self, value, user, room):
        self.value=value
        self.user=user
        self.room=room
        db.session.add(self)
        db.session.commit()

    def dict(self, **kwargs):
        return {
            'user': self.user.dict(),
            'room': self.room.id,
            'value': self.value
        }

    @staticmethod
    def get_replies(id):
        return Message.query.get(id).replies

    def replied(self, message):
        return self.messages.filter(
            message_replies.c.message == message.id
        ).count() > 0

    def reply(self, message):
        if not self.replied(message):
            self.messages.append(message)
            db.session.commit()
