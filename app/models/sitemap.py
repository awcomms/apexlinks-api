from datetime import datetime, timezone
import sys
import gzip
import xml.etree.ElementTree as ET

from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.vars import api_host, sitemap_attribs, sitemap_entry_limit, sitemap_byte_limit
from app.misc.datetime_period import datetime_period
from app.models.mod import Mod

from datetime import datetime, timezone

class Sitemap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sitemap_index_id = db.Column(db.Integer, db.ForeignKey('sitemap_index.id'))
    pages = db.relationship('SitePage', backref='sitemap', lazy='dynamic')
    users = db.relationship('User', backref='sitemap', lazy='dynamic')
    mods = db.relationship('Mod', backref='sitemap', lazy='dynamic')
    type = db.Column(db.Unicode)

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
    def add_new_page(page):
        query = Sitemap.query.filter_by(type='page')
        sitemap = query.filter(Sitemap.willbefull(page) == False).first()
        if not sitemap:
            sitemap = SitemapIndex.create_sitemap('page')
        sitemap.add_page(page)

    def lastmod(self):
        # return most recent of self.mods
        return self.mods.order_by(Mod.datetime.desc()).first()

    def __init__(self, type='user'):
        self.type = type
        db.session.add(self)
        db.session.commit()

    def url(self):
        return f'{api_host}/sitemap/{self.id}'

    @staticmethod
    def willnotbefull(instance, type='user'):
        if type != 'page' or type != 'user':
            type = 'user'
        query = Sitemap.query.filter_by(type=type)
        for sitemap in query:
            if type=='user':
                count = sitemap.users.count()
            elif type=='page':
                count = sitemap.pages.count()
            else:
                count = sitemap.pages.count()
            if not count < sitemap_entry_limit:
                continue

            xml = sitemap.xml()
            instance_xml = instance.xml()
            xml.append(instance_xml)

            string = ET.tostring(xml, encoding='utf-8')
            _bytes = bytes(string)
            zip = gzip.compress(_bytes)
            zip_size = sys.getsizeof(zip)

            if not zip_size < sitemap_byte_limit:
                continue
            return sitemap
    
    @hybrid_property
    def willbefull(self, instance):
        """
            second checkSimulates adding instance's xml to self
            then checks the resulting zip size
        """
        if not self.users.count() + self.pages.count() < sitemap_entry_limit:
            return True
        xml = self.xml()
        ET.SubElement(xml, instance.xml())
        return not sys.getsizeof(gzip.compress(bytes(ET.tostring(xml, encoding='utf-8'), 'utf-8'))) < sitemap_byte_limit

    def page_added(self, page):
        return self.pages.filter_by(id=page.id).count() > 0

    def add_page(self, page):
        if not self.page_added():
            self.pages.append(page)
            self.new_mod()
            db.session.commit()

    def remove_page(self, page):
        if not self.page_added():
            self.pages.remove(page)
            self.new_mod()
            db.session.commit()

    def user_added(self, user):
        return self.users.filter_by(id=user.id).count() > 0

    def add_user(self, user):
        if not self.user_added(user):
            self.users.append(user)
            self.new_mod()
            db.session.commit()

    def remove_user(self, user):
        if not self.user_added(user):
            self.users.remove(user)
            self.new_mod()
            db.session.commit()

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def xml(self):
        map = ET.Element('urlset', sitemap_attribs)
        for page in self.pages:
            entry = ET.Element('url')

            loc = ET.Element('loc')
            loc.text = page.url()
            entry.append(loc)

            lastmod = ET.Element('lastmod')
            lastmod.text = str(page.lastmod())
            entry.append(lastmod)

            changefreq = ET.Element('changefreq')
            changefreq.text = page.changefreq()
            entry.append(changefreq)

            priority = ET.Element('priority')
            priority.text = page.priority
            entry.append(priority)

            map.append(entry)
        for user in self.users:
            entry = ET.Element('url')

            loc = ET.Element('loc')
            loc.text = user.url()
            entry.append(loc)

            lastmod = ET.Element('lastmod')
            lastmod.text = str(user.lastmod())
            entry.append(lastmod)

            changefreq = ET.Element('changefreq')
            changefreq.text = user.changefreq()
            entry.append(changefreq)

            priority = ET.Element('priority')
            priority.text = user.priority
            entry.append(priority)

            map.append(entry)
        return map

    def xml_string(self):
        return ET.tostring(self.xml(), encoding='utf-8')

    def gzip(self):
        return gzip.compress(bytes(self.xml_string), 'utf-8')

from app.user_model import User
from app.models.sitemap_index import SitemapIndex