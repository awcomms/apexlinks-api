from app import db

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)