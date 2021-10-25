from app import db

class Taggroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    tags = db.relationship('Tag', backref='taggroup', lazy='dynamic')

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()