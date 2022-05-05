from datetime import datetime, timezone
from sqlalchemy.orm import backref
from app.models.mod import Mod
from app.models.sitemap_index import SitemapIndex
from app import db
from fuzzywuzzy import process, fuzz
from app.vars.q import host, global_priority
from app.misc.fields import score
from app.misc.datetime_period import datetime_period
import xml.etree.ElementTree as ET
from app.models.user import User

item_items = db.Table('item_items',
                      db.Column('parent', db.Integer,
                                db.ForeignKey('item.id')),
                      db.Column('child', db.Integer, db.ForeignKey('item.id')))


class Item(db.Model):
    tags = db.Column(db.JSON)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hidden = db.Column(db.Boolean, default=False)
    # folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    image = db.Column(db.Unicode)
    embed = db.Column(db.Unicode)
    choices = db.Column(db.JSON)
    options = db.Column(db.JSON)
    fields = db.Column(db.JSON)
    distance = db.Column(db.JSON)
    images = db.Column(db.JSON)
    link = db.Column(db.Unicode)
    redirect = db.Column(db.Boolean, default=False)
    itype = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    itext = db.Column(db.Unicode)
    score = db.Column(db.Float)

    items = db.relationship('Item', secondary=item_items, primaryjoin=id ==
                            item_items.c.parent, secondaryjoin=id == item_items.c.child, backref=db.backref('parents', lazy='dynamic'), lazy='dynamic')

    def item_added(self, item):
        return self.items.filter(
            item_items.c.child == item.id
        ).count() > 0

    def add_item(self, item):
        if not self.item_added(item):
            self.items.append(item)
            db.session.commit()

    def remove_item(self, item):
        if self.item_added(item):
            self.items.remove(item)
            db.session.commit()

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
        if hasattr(self, 'username'):
            return f'{host}/u/{self.username}'
        else:
            return f'{host}/i/{self.id}'

    @staticmethod
    def fuz(query, fields, tags):
        fields = fields or []
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

    def min_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user': {
                'username': self.user.username,
                'id': self.user.id
            },
            'options': self.options,
            'tags': self.tags,
            'choices': self.choices
        }

    def dict(self, **kwargs):
        res = {
            'id': self.id,
            'name': self.name,
            'tags': self.tags,
            'itype': self.itype,
            'link': self.link,
            'itext': self.itext,
            'image': self.image,
            'images': self.images,
            'options': self.options,
            'time': str(self.time),
            'type': type(self).__name__.lower(),
            'fields': self.fields,
            'hidden': self.hidden,
            'user': {
                'username': self.user.username,
                'id': self.user.id
            },
            'redirect': self.redirect,
            'parents': [i.min_dict() for i in self.parents],
            'children': [i.min_dict() for i in self.items]
        }

        if 'user' in kwargs and kwargs['user'] and 'attrs' in kwargs:
            user = kwargs['user']
            print('.__attrs', kwargs['attrs'])
            for attr in kwargs['attrs']:
                if attr == 'saved':
                    res[attr] = user.item_saved(self)
                    continue
                if hasattr(user, attr):
                    res[attr] = getattr(user, attr)
                else:
                    # TODO-error
                    pass
        return res

    def __init__(self, data, now=True):
        if not 'name' in [f['label'] for f in data['fields']]:
            data['fields'].append({'label': 'name', 'value': ''})
        for field in data:
            if hasattr(self, field) and data[field]:
                setattr(self, field, data[field])
        if not 'tags' in data:
            self.tags = []
        
        db.session.add(self)
        if now:
            db.session.commit()
        self.new_mod()
        SitemapIndex.add_item(self)

    def edit(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
        db.session.commit()
