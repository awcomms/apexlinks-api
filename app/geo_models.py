from app import db
from app.models import Query
from sqlalchemy_utils.types import TSVectorType

class Place(db.Model):
    query_class = Query
    name = db.Column(db.Unicode)
    tags = db.Column(db.Unicode)
    coordinates = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    search_vector = db.Column(TSVectorType('tags', 'name', weights={'tags': 'A', 'name': 'B'}))
    users = db.relationship('User', backref='place', lazy='dynamic')
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    town_id = db.Column(db.Integer, db.ForeignKey('town.id'))

    @staticmethod
    def is_saved(id, user_id):
        user = User.query.get(user_id)
        if not user:
            return False
        return user.saved_places.filter_by(id=id).count()>0

    def add_tag(self, tag):
        self.tags += ', ' + tag
        db.session.commit()

    def dict(self):
        if self.tags:
            tags = self.tags.split(', ')
        data = {
            'id': self.id,
            'tags': self.tags,
            'name': self.name,
            'coordinates': self.coordinates
        }
        return data

    def __init__(self, name, state):
        self.state = state
        self.name = name
        db.session.add(self)
        db.session.commit()

class Town(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    places = db.relationship('Place', backref='town', lazy='dynamic')
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'state': self.state.dict()
        }

    def __init__(self, name, state):
        self.name = name
        self.state = state
        db.session.add(self)
        db.session.commit()

class State(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    places = db.relationship('Place', backref='state', lazy='dynamic')
    towns = db.relationship('Town', backref='state', lazy='dynamic')
    nation_id = db.Column(db.Integer, db.ForeignKey('nation.id'), nullable=False)

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'nation': self.nation.dict()
        }

    def __init__(self, name, nation):
        self.name = name
        self.nation = nation
        db.session.add(self)
        db.session.commit()

class Nation(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    states = db.relationship('State', backref='nation', lazy='dynamic')

    def dict(self):
        data = {
            'id': self.id,
            'name': self.name,
        }

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()
