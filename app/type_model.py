from sqlalchemy.orm import backref
from app import db

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    fields = db.Column(db.JSON)
    # fields = db.relationship('Field', backref='type', lazy='dynamic')