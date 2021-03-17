from app import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    body = db.Column(db.Unicode)
    timestamp = db.Column(db.Unicode)

    def __init__(self, body, user, group):
        self.body=body
        self.user=user
        self.group=group
        db.session.add(self)
        db.session.commit()