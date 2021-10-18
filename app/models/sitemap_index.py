import io, sys, gzip
import xml.etree.ElementTree as ET

from zipfile import ZipFile

from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import backref
from app import db
from app.vars import api_host, sitemapindex_attribs, sitemap_entry_limit, sitemap_byte_limit
from datetime import datetime, timezone
from app.models.sitemap import Sitemap

class SitemapIndex(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mods = db.relationship('Mod', backref='sitemap_index', lazy='dynamic')
    sitemaps = db.relationship('Sitemap', backref='index', lazy='dynamic')
    lastmod = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    loc = db.Column(db.Unicode)

    # TODO edit lastmod on sitemap add or remove

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def url(self):
        return f'{api_host}/{self.id}'

    @staticmethod
    def add_user(user):
        sitemap = Sitemap.query.filter(Sitemap.willbefull(user) == False).first()
        if not sitemap:
            sitemap = SitemapIndex.create_sitemap()
        sitemap.add_user(user)

    @staticmethod
    def create_sitemap():
        sitemap = Sitemap()
        index = SitemapIndex.query.filter(SitemapIndex.willbefull(sitemap) == False).first()
        if not index:
            index = SitemapIndex()
        index.add_sitemap(sitemap)
        return sitemap

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
        return not sys.getsizeof(gzip.compress(bytes(ET.tostring(xml, encoding='utf-8'), 'utf-8'))) < sitemap_byte_limit

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()
    
    def sitemap_added(self, sitemap):
        return self.sitemaps.filter_by(id=sitemap.id).count()>0

    def add_sitemap(self, sitemap):
        if not self.sitemap_added():
            self.sitemaps.append(sitemap)
            self.new_mod()
            db.session.commit()

    def remove_sitemap(self, sitemap):
        if not self.sitemap_added():
            self.sitemaps.remove(sitemap)
            self.new_mod()
            db.session.commit()

    def xml(self):
        index = ET.Element('sitemapindex', sitemapindex_attribs)
        for sitemap in self.sitemaps:
            entry = ET.Element('sitemap')

            loc = ET.Element('loc')
            loc.text = sitemap.url()
            ET.SubElement(entry, loc)

            lastmod = ET.Element('lastmod')
            lastmod.text = sitemap.lastmod()
            ET.SubElement(entry, lastmod)

            ET.SubElement(index, entry)
        return index

    def xml_string(self):
        return ET.tostring(self.xml(), encoding='utf-8')

    def file(self):
        return io.StringIO(self.xml_string())

    def zip(self):
        return ZipFile(self.file(), force_zip64=True)

    def zip_size(self):
        return sum([zinfo.compress_size for zinfo in self.zip().infolist()])