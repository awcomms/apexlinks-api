from app import db

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    taggroup_id = db.Column(db.Integer, db.ForeignKey('taggroup.id'))

    def __init__(self, name, taggroup=None):
        self.name = name
        self.taggroup = taggroup
        db.session.add(self)
        db.session.commit()