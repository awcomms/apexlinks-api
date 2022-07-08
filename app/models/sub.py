from app import db

class Sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user, sub):
        self.sub = sub
        self.user = user
        db.session.add(self)
        db.session.commit()