from flask import send_file
from app.models.sitemap import Sitemap
from app.routes import bp

@bp.route('/sitemap/<int:id>')
def get_sitemap(id):
    sitemap = Sitemap.query.get(id)
    if not sitemap:
        return '', 404
    return send_file(sitemap.gzip())