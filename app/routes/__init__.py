from flask import Blueprint

bp = Blueprint('api', __name__)

from . import \
    sitemap,\
    sitemap_index,\
    robots_txt,\
    subs,\
    items,\
    rooms,\
    users,\
    tokens,\
    messages