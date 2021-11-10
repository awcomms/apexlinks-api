from app import db
from app.misc.countries.get import countries

class C(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    taken = db.Column(db.Boolean, default=False)

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'taken': self.taken
        }

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()
        self.new_mod()
        db.session.commit()

for _c in countries():
    name = _c['name']
    if not C.query.filter_by(name=name).first():
        C(name)