from app import db

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    notes = db.relationship('Note', backref='level', lazy='dynamic')
    users = db.relationship('User', backref='level', lazy='dynamic')

    def dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()