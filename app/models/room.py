from app import db
from fuzzywuzzy import process
from app.models.junctions import xrooms
from app.vars.q import room_search_fields
from app.misc.sort.tag_sort import tag_sort

class Room(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    open = db.Column(db.Boolean, default=False)
    one = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # rooms = db.relationship('Room', backref=db.backref('room', lazy='dynamic'))
    messages = db.relationship('Message', backref='room', lazy='dynamic')
    name = db.Column(db.Unicode)
    unseen = db.Column(db.Boolean, default=False)

    @staticmethod
    def get(tags, limit=0):
        def tag_score(items): return tag_sort(room_search_fields, items, tags)
        _sort = tag_score
        
        def filter(items):
            for idx, item in enumerate(items):
                if item['score'] < limit:
                    items.pop(idx)
            return items

        def run(items):
            _items = _sort(items)
            if limit:
                _items = filter(_items)
            return _items

        return run

    def dict(self, **kwargs):
        uid = None
        seen = None
        if 'user' in kwargs:
            uid = kwargs['user'].id
        row = db.engine.execute(xrooms.select().where(xrooms.c.user_id == uid)
                                .where(xrooms.c.room_id == self.id)).first()
        if row:
            seen = row['seen']
        data = {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'open': self.open,
            'user': self.user.dict()
        }
        if seen is False:
            data['unseen'] = True
        if not self.open:
            data['users'] = [user.username for user in self.users]
        return data

    def __init__(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.add(self)
        db.session.commit()

    def edit(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.commit()
