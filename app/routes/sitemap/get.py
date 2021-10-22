import io
from flask import send_file
from app.models.sitemap import Sitemap
from app.routes import bp

@bp.route('/sitemap/<int:id>')
def get_sitemap(id):
    sitemap = Sitemap.query.get(id)
    if not sitemap:
        return '', 404
    f = io.BytesIO(bytes(sitemap.xml_string()))
    f.seek(0)
    return send_file(f, mimetype='application/txt')