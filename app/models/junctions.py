from app import db

answered = db.Table('answered',
                    db.Column('q', db.Integer, db.ForeignKey('q.id')),
                    db.Column('id', db.Integer, db.ForeignKey('option.id')),
    )

xtxts = db.Table('xtxts',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                  db.Column('txt_id', db.Integer, db.ForeignKey('txt.id')),
                  db.Column('notify', db.JSON, default=True),
                  db.Column('seen', db.Boolean))
