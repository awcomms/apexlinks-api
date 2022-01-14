from app import db

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    value = db.Column
    
    def __init__(self, text):
        self.text = text
        db.session.add(self)
        db.session.commit()
    