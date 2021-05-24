from app import db

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('Item', backref='folder', lazy='dynamic')
    folders = db.relationship('Folder', backref='folder', lazy='dynamic')

    def __init__(self, name, user):
        self.name = name
        self.user = user
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user": self.user.username,
            "item_count": self.items.count(),
            "folder_count": self.folders.count()
        }