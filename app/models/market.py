from app import db

class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    users = db.relationship('User', backref='market', lazy='dynamic')
    postalAddress = db.Column(db.JSON)

    def __init__(self, postalAddress):
        self.postalAddress = postalAddress
        db.session.add(self)
        db.session.commit()

    def user_added(self, user):
        return self.users.filter_by(id=user.id).count() > 0

    def add_user(self, user):
        if not self.user_added(user):
            self.users.append(user)
            db.session.commit()

    def remove_user(self, user):
        if self.user_added(user):
            self.users.remove(user)
            db.session.commit()
