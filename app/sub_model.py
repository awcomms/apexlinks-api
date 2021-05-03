from app import db

class Sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.JSON)
    endpoint = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user, endpoint, sub):
        self.sub = sub
        self.endpoint = endpoint
        self.user = user
        db.session.add(self)
        db.session.commit()