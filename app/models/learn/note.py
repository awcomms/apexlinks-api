from app import db
from app.models.mod import Mod
from datetime import datetime, timezone

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    name = db.Column(db.Unicode)
    mods = db.relationship('Mod', backref='note', lazy='dynamic')
    body = db.Column(db.Unicode)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __init__(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.add(self)
        db.session.commit()

    def last_modification(self):
        return self.mods.order_by(Mod.datetime.desc()).first()

    def lastmod(self):
        str(self.last_modification())

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()
        self.new_mod()
        db.session.commit()

    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'body': self.body,
            'created': str(self.time),
            'lastmod': self.lastmod(),
            # 'level': self.level_id
        }
