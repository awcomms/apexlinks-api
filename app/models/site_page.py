from app import db
from datetime import datetime, timezone

disallow = [
    'add_item',
    'add_room',
    'edit',
    'reset_password'
]

class SitePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    lastmod = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    mods = db.relationship('Mod', backref='site_page', lazy='dynamic')
    changefreq = db.Column(db.Unicode)
    disallow = db.Column(db.Boolean)

    def changefreq(self):
        

    def __init__(self):
        if self.name in disallow:
            self.disallow = True
        db.session.add(self)
        db.session.commit()

    def edit_last_mod(date):
        """
            TODO function to edit last mod on frontend push
        """
        pass

    def edit_changefreq():
        """
            TODO function to calculate average changefreq from all lastmods
        """
        pass