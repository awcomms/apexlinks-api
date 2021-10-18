import io, sys, gzip
import xml.etree.ElementTree as ET

from zipfile import ZipFile

from sqlalchemy.ext.hybrid import hybrid_method
from app import db
from app.vars import api_host, sitemap_attribs, sitemap_entry_limit, sitemap_byte_limit
from datetime import datetime, timezone
from app.models.sitemap import Sitemap
from app.models.mod import Mod

class Sitemap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='sitemap', lazy='dynamic')
    mods = db.relationship('Mod', backref='sitemap', lazy='dynamic')

    # TODO edit lastmod on sitemap add or remove

    def lastmod(self):
        # return most recent of self.mods
        return self.mods.order_by(Mod.date.desc()).first()

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def url(self):
        return f'{api_host}/{self.id}'

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

    def user_added(self, user):
        return self.user.filter_by(id=user.id).count()>0

    def add_user(self, user):
        if not self.user_added():
            self.users.append(user)
            self.new_mod()
            db.session.commit()

    def remove_user(self, user):
        if not self.user_added():
            self.users.remove(user)
            self.new_mod()
            db.session.commit()

    def new_mod(self):
        mod = Mod()
        self.mods.append(mod)
        db.session.commit()

    def xml(self):
        map = ET.Element('urlset', sitemap_attribs)
        for user in self.users:
            entry = ET.Element('url')

            loc = ET.Element('loc')
            loc.text = user.sitemap_loc()
            ET.SubElement(entry, loc)

            lastmod = ET.Element('lastmod')
            lastmod.text = str(user.lastmod)
            ET.SubElement(entry, lastmod)

            changefreq = ET.Element('changefreq')
            changefreq.text = user.changefreq()
            ET.SubElement(entry, changefreq)

            priority = ET.Element('priority')
            priority.text = '0.7'
            ET.SubElement(entry, priority)

            ET.SubElement(map, entry)
        return map

    def xml_string(self):
        return ET.tostring(self.xml(), encoding='utf-8')

    def file(self):
        return io.StringIO(self.xml_string())

    def zip(self):
        return ZipFile(self.file(), force_zip64=True)

    def zip_size(self):
        return sum([zinfo.compress_size for zinfo in self.zip().infolist()])