from app import db
from datetime import datetime, timezone

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))
    sitemap_index_id = db.Column(db.Integer, db.ForeignKey('sitemap_index.id'))

    def __init__(self):
        db.session.add(self)
        db.session.commit()