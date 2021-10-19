from app import db
from app.models.mod import Mod
from app.misc.datetime_period import datetime_period

disallow = [
    'add_item',
    'add_room',
    'edit',
    'reset_password'
]


class SitePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))
    mods = db.relationship('Mod', backref='site_page', lazy='dynamic')
    disallow = db.Column(db.Boolean)

    def last_modification(self):
        return self.mods.order_by(Mod.datetime.desc()).first()

    def lastmod(self):
        str(self.last_modification())

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def changefreq(self):
        differences = []
        query = self.mods.order_by(Mod.datetime.asc())
        previous_mod = None
        for mod in query:
            if not previous_mod:
                previous_mod = mod
                continue
            differences.append(mod-previous_mod.total_seconds())
            previous_mod = mod
        average = sum(differences) / len(differences)
        return datetime_period(average)

    def __init__(self, name):
        if name == 'login':
            self.priority = 1
        else:
            self.priority = 0.7
        if self.name in disallow:
            self.disallow = True
        db.session.add(self)
        db.session.commit()
