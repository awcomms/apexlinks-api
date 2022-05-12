from fuzzywuzzy import fuzz
from app import db

de = db.engine.execute

tags = db.Table('tags',
    db.Column('l', db.Integer),
    db.Column('r', db.Integer, db.Fore),
    db.Column('s', db.Unicode))


def added(v):
    return de(tags.select().where(tags.c.l == v).count()) > 0

def linked

def add(v):
    if added(v): return
    de(tags.insert().values(l=v))
    pass

def link(l, r):
    if l == r:
        return None
    if not added(l):
        add(l)
    if not added(r):
        add(r)
    de(tags.update().where(tags.c.l == l).values(r=r, score=fuzz.ratio(l, r)))
    pass

def unlink(l, r):
    pass