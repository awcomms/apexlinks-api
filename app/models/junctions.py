from app import db

xrooms = db.Table('xrooms',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
                  db.Column('seen', db.Boolean))
