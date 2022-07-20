from app import db

q_options = db.Table('q_options',
    db.Column('q', db.Integer, db.ForeignKey('q.id')),
    db.Column('option', db.Integer, db.ForeignKey('option.id')),
    db.Column('answer', db.Integer, db.ForeignKey('option.id')))

class Q(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)
    options = db.relationship('Option', secondary=q_options, backref=db.backref('q', lazy='dynamic'), lazy='dynamic')