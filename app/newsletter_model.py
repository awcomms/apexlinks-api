from datetime import datetime
from app import db

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Unicode)
    body = db.Column(db.Unicode)

    def __init__(self, slug, body):
        self.slug = slug
        self.body = body
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'body': self.body
        }