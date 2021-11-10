from app import db
from datetime import datetime, timezone

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, src):
        self.src = src
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            'id': self.id,
            'src': self.src
        }