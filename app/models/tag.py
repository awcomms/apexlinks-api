from app import db

tags = db.Table(
    db.Column('l', db.Unicode, db.ForeignKey('tag.value')),
    db.Column('r', db.Unicode, db.ForeignKey('tag.value')),
    db.Column('score', db.Float)
)


def score(l, r):
    db.engine.execute(tags.select().where(tags.c.l == l))
    db.engine.execute(tags.select().where(tags.c.l == l)
                                    .where(tags.c.txt_id == self.id)).first()