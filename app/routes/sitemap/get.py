from flask import send_file
from flask.helpers import send_from_directory, url_for
from app.models.sitemap import Sitemap
from app.routes import bp

@bp.route('/base_sitemap')
def base_sitemap():
    return send_from_directory(url_for('static', filename='base_sitemap.xml'))

@bp.route('/sitemap/<int:id>')
def get_sitemap(id):
    sitemap = Sitemap.query.get(id)
    if not sitemap:
        return '', 404
    return send_file(sitemap.gzip)