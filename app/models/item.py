from app import db
from fuzzywuzzy import process, fuzz
from app.vars.q import host, global_priority
from app.misc.fields.score import field_score
from app.misc.datetime_period import datetime_period
import xml.etree.ElementTree as ET
from app.models.user import User

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

    mods = db.relationship('Mod', backref='item', lazy='dynamic')
    sitemap_id = db.Column(db.Integer, db.ForeignKey('sitemap.id'))

    def xml(self):
        entry = ET.Element('url')

        loc = ET.Element('loc')
        loc.text = self.url()
        entry.append(loc)

        lastmod = ET.Element('lastmod')
        lastmod_date = self.lastmod
        lastmod_str = str(lastmod_date)
        lastmod.text = lastmod_str
        entry.append(lastmod)

        changefreq = ET.Element('changefreq')
        changefreq.text = self.changefreq()
        entry.append(changefreq)

        priority = ET.Element('priority')
        priority.text = global_priority
        entry.append(priority)

        return entry
    
    def last_modification(self):
        return self.mods.order_by(Mod.datetime.desc()).first()

    def lastmod(self):
        str(self.last_modification())

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def changefreq(self):
        differences = []
        query = self.mods.order_by(Mod.datetime.asc())
        previous_mod = None
        for mod in query:
            if not previous_mod:
                previous_mod = mod
                continue
            differences.append(mod-previous_mod.total_seconds())
            previous_mod = mod
        if len(differences):
            average = sum(differences) / len(differences)
            period = datetime_period(average)
            print('dp', period)
            return period
        else:
            return 'always'

    def url(self):
        return f'{host}/{self.username}'

    @staticmethod
    def fuz(market_id, fields, user, id, hidden, tags):
        fields = fields or []
        query = Item.query.join(User)
        if market_id:
            query = query.filter(User.market_id == market_id)
        if not id:
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
            item.score = 0
            if isinstance(item.tags, list) and tags:
                for tag in tags:
                    try:
                        item.score += process.extractOne(
                            tag, item.tags + item.attr_tags())[1]
                    except:
                        pass
            # if item.fields:
            #     item.score += field_score(item.fields, fields)
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
            'user': self.user.dict(),
            'redirect': self.redirect,
            'user': self.user.username
        }

    def __init__(self, data):
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        db.session.add(self)
        db.session.commit()
        self.new_mod()
        SitemapIndex.add_item(self)

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()

from app.models.sitemap_index import SitemapIndex
from app.models.mod import Mod