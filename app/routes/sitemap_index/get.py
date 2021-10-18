from flask import send_file
from app.models.sitemap_index import SitemapIndex
from app.routes import bp

@bp.route('/sitemap_index/<int:id>')
def get_sitemap_index(id):
    sitemap_index = SitemapIndex.query.get(id)
    if not sitemap_index:
        return '', 404
    return send_file(sitemap_index.gzip())