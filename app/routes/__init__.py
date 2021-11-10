from flask import Blueprint

bp = Blueprint('api', __name__)

from . import \
    sitemap,\
    sitemap_index,\
    robots_txt,\
    pay,\
    subs,\
    items,\
    rooms,\
    users,\
    tokens,\
    messages,\
    world,\
    markets
from . import c, world, learn, sitemap, sitemap_index, robots_txt, pay, subs, items, rooms, users, tokens, messages
