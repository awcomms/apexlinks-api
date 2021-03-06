import sys
import gzip
import xml.etree.ElementTree as ET

from app.misc.datetime_period import datetime_period
from sqlalchemy.ext.hybrid import hybrid_method
from app import db
from app.vars.q import api_host, sitemapindex_attribs, sitemap_entry_limit, sitemap_byte_limit
from app.misc.now import now
from app.models.mod import Mod


class SitemapIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mods = db.relationship('Mod', backref='sitemap_index', lazy='dynamic')
    sitemaps = db.relationship('Sitemap', backref='index', lazy='dynamic')
    lastmod = db.Column(db.DateTime, default=now())
    loc = db.Column(db.Unicode)

    # TODO edit lastmod on sitemap add or remove

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def url(self):
        return f'{api_host}/sitemap_index/{self.id}'

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
        average = sum(differences) / len(differences)
        return datetime_period(average)

    @staticmethod
    def add_user(user):
        sitemap = Sitemap.willnotbefull(user)
        print('s', sitemap)
        if not sitemap:
            sitemap = SitemapIndex.create_sitemap()
        sitemap.add_user(user)

    @staticmethod
    def add_item(item):
        sitemap = Sitemap.willnotbefull(item)
        if not sitemap:
            sitemap = SitemapIndex.create_sitemap(type='item')
        sitemap.add_item(item)

    @staticmethod
    def create_sitemap(type='user'):
        sitemap = Sitemap(type)
        index = SitemapIndex.willnotbefull(sitemap)
        if not index:
            index = SitemapIndex()
        index.add_sitemap(sitemap)
        return sitemap

    @staticmethod
    def willnotbefull(sitemap):
        for si in SitemapIndex.query:
            if not si.maps.count() < sitemap_entry_limit:
                continue
            xml = si.xml()
            xml.append(sitemap.xml())
            
            string = ET.tostring(xml, encoding='utf-8')
            bytes = bytes(string, 'utf-8')
            zip = gzip.compress(bytes)
            zip_size = sys.getsizeof(zip)
            if not zip_size < sitemap_byte_limit:
                continue
            return si

    @hybrid_method
    def willbefull(self, sitemap):
        """
            second checkSimulates adding sitemap's xml to self
            then checks the resulting zip size
        """
        if not self.maps.count() < sitemap_entry_limit:
            return True
        xml = self.xml()
        ET.SubElement(xml, sitemap.xml())
        return 

    def last_modification(self):
        return self.mods.order_by(Mod.datetime.desc()).first()

    def lastmod(self):
        str(self.last_modification())

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def sitemap_added(self, sitemap):
        return self.sitemaps.filter_by(id=sitemap.id).count() > 0

    def add_sitemap(self, sitemap):
        if not self.sitemap_added(sitemap):
            self.sitemaps.append(sitemap)
            self.new_mod()
            db.session.commit()

    def remove_sitemap(self, sitemap):
        if not self.sitemap_added(sitemap):
            self.sitemaps.remove(sitemap)
            self.new_mod()
            db.session.commit()

    def xml(self):
        index = ET.Element('sitemapindex', sitemapindex_attribs)
        for sitemap in self.sitemaps:
            entry = ET.Element('sitemap')

            loc = ET.Element('loc')
            loc.text = sitemap.url()
            entry.append(loc)

            lastmod = ET.Element('lastmod')
            lastmod.text = sitemap.lastmod()
            entry.append(lastmod)

            index.append(entry)
        return index

    def xml_string(self):
        return ET.tostring(self.xml(), encoding='utf-8')

    def gzip(self):
        xml_string = self.xml_string()
        _bytes = bytes(xml_string)
        zip = gzip.compress(_bytes)
        return zip

from app.models.sitemap import Sitemap