from app import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    notes = db.relationship('Note', backref='subject', lazy='dynamic')
    results = db.relationship('Result', backref='subject', lazy='dynamic')

    def dict(self):
        return {
            'id': self.id,
            'text': self.name,
            'name': self.name
        }

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()