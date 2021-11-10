import sys
import xml.etree.ElementTree as ET
from gzip import compress
from app.vars.q import sitemap_byte_limit

def xml_string(instance):
    return ET.tostring(instance.xml(), encoding='utf-8')

def file(instance):
    return open(xml_string(instance))

def zip(instance):
    return compress(bytes(xml_string(instance)), 'utf-8')

def zip_size(instance):
    return sys.getsizeof(zip(instance))

def max_zip_size(instance):
    return zip_size(instance) >= sitemap_byte_limit