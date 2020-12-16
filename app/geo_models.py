from app import db
from app.models import Query
from sqlalchemy_utils.types import TSVectorType

class Place(db.Model):
    query_class = Query
    name = db.Column(db.Unicode)
    coordinates = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    search_vector = db.Column(TSVectorType('name'))
    users = db.relationship('User', backref='place', lazy='dynamic')
    town_id = db.Column(db.Integer, db.ForeignKey('town.id'), nullable=False)

    def dict(self):
        data = {
            'id': self.id,
            'text': self.name,
            'coordinates': self.coordinates
        }
        return data

    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates
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
        db.sesion.add(self)
        db.session.commit()

class State(db.Model):
    query_class = Query
    search_vector = db.Column(TSVectorType('name'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
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
        db.sesion.add(self)
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
        db.sesion.add(self)
        db.session.commit()
