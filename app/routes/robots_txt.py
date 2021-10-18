import io

from flask.helpers import send_file, url_for
from app.models.site_page import SitePage
from app.routes import bp
from app.misc.newline_write import newline_write
from app.models.sitemap_index import SitemapIndex

@bp.route('/robots.txt', methods=['GET'])
def get_robots_txt():
    f = io.BytesIO()
    newline_write(f, 'User-Agent: *')
    for page in SitePage.query.filter_by(disallow=True):
        newline_write(f'Disallow: /{page.name}')
    for sitemap_index in SitemapIndex.query:
        print(sitemap_index)
        newline_write(f, f'Sitemap: {sitemap_index.url()}',)
    return send_file(f, mimetype='application/txt')