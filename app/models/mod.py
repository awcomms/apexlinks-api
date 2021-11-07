from app import db
from datetime import datetime, timezone

class Mod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    site_page_id = db.Column(db.Integer, db.ForeignKey('site_page.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))
    sitemap_index_id = db.Column(db.Integer, db.ForeignKey('sitemap_index.id'))

    def __init__(self):
        db.session.add(self)
        db.session.commit()