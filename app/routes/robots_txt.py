import io

from flask.helpers import send_file, url_for
from app.models.site_page import SitePage
from app.routes import bp
from app.misc import newline_write
from app.models.sitemap_index import SitemapIndex

@bp.route('/robots.txt', methods=['GET'])
def get_robots_txt():
    f = open(url_for('static', filename='site.robots.txt'), 'a')
    newline_write(f, 'User-Agent: *')
    for page in SitePage.query.filter_by(disallow=True):
        newline_write(f'Disallow: /{page.name}')
    for sitemap_index in SitemapIndex.query:
        newline_write(f, f'Sitemap: {sitemap_index.loc}',)
    return send_file(f)