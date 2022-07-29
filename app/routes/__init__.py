from flask import Blueprint

bp = Blueprint('api', __name__)

@bp.route('healthcheck')
def healthcheck():
    return '', 200

from . import \
    sitemap,\
    sitemap_index,\
    robots_txt,\
    subs,\
    items,\
    txts,\
    users,\
    tokens,\
    txts