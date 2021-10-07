from app import db
from fuzzywuzzy import process, fuzz
from app.user_model import User

class Item(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hidden = db.Column(db.Boolean, default=False)
    # folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    image = db.Column(db.Unicode)
    fields = db.Column(db.JSON)
    distance = db.Column(db.JSON)
    images = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    redirect = db.Column(db.Boolean, default=False)
    itype = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    itext = db.Column(db.Unicode)
    score = db.Column(db.Float)

    @staticmethod
    def fuz(fields, user, id, hidden, tags):
        fields = fields or []
        query = Item.query.join(User)
        if not id:
            # query = query.filter(User.paid==True) #TODO deactivate for production
            query = query.filter(User.hidden==False)
            query = query.filter(Item.hidden==False)
        elif id:
            query = query.filter(User.id==id)
            if user:
                try:
                    query = query.filter(Item.hidden==hidden)
                except:
                    pass
        for item in query:
            if item.fields:
                for field in fields:
                    try:
                        labelCutoff = int(field['labelCutoff'])
                    except:
                        labelCutoff = 90
                    try:
                        valueCutoff = int(field['valueCutoff'])
                    except:
                        valueCutoff = 90
                    item.score = 0
                    itemFieldlabels = []
                    for itemField in item.fields:
                        itemFieldlabels.append(itemField['label'])
                    result = process.extractOne(field['label'], itemFieldlabels, scorer=fuzz.partial_ratio)
                    if not result:
                        continue
                    elif result[1] < labelCutoff:
                        pass
                        # query = query.filter(Item.id != item.id)
                    else:
                        if not 'type' in field or field['type'] == 'text':
                            value = ''
                            for itemField in item.fields:
                                if itemField['label'] == result[0]:
                                    value = itemField['value']
                            score = fuzz.partial_ratio(field['value'], value)
                            if score >= valueCutoff:
                                item.score += score
            if isinstance(item.tags, list) and tags:
                for tag in tags:
                    try:
                        item.score += process.extractOne(tag, item.tags)[1]
                    except:
                        pass
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
            'fields': self.fields,
            'hidden': self.hidden,
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