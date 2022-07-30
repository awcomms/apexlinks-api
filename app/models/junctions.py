from app import db

xtxts = db.Table('xtxts',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('txt_id', db.Integer, db.ForeignKey('txt.id')),
                  db.Column('notify', db.JSON, default=True),
                  db.Column('seen', db.Boolean))
