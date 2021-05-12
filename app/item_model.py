from app import db
from fuzzywuzzy import process, fuzz
from app.user_model import User

class Item(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visible = db.Column(db.Boolean, default=True)
    image = db.Column(db.Unicode)
    data = db.Column(db.Unicode)
    images = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    redirect = db.Column(db.Boolean, default=True)
    itype = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    itext = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(user, id, visible, tags):
        query = Item.query.join(User)
        if not id:
            query = query.filter(User.paid==True)
            query = query.filter(User.visible==True)
        elif id:
            query = query.filter(User.id==id)
        try:
            query = query.filter(Item.visible==visible)
        except:
            pass
        item_tag_score = 0 #TODO optimize
        user_tag_score = 0
        for item in query:
            for tag in tags:
                item_tag_score += process.extractOne(tag, item.tags, scorer=fuzz.partial_ratio)[1]
            if user:
                for tag in user.tags:
                    user_tag_score += process.extractOne(tag, item.user.tags, scorer=fuzz.partial_ratio)[1]
                item.score = item_tag_score * user_tag_score
            else:
                item.score = item_tag_score
        db.session.commit()
        query = query.order_by(Item.score.desc())
        return query

    def dict(self, **kwargs):
       return {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'itype': self.itype,
            'link': self.link,
            'itext': self.itext,
            'image': self.image,
            'images': self.images,
            'visible': self.visible,
            'redirect': self.redirect,
            'user': self.user.username
        }

    def __init__(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.add(self)
        db.session.commit()

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()