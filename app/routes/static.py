from werkzeug.utils import send_from_directory
from app.routes import bp
from flask import current_app


@bp.route('/directory-sitemap', methods=['GET'])
def directory_sitemap():
    return send_from_directory(current_app.config['UPLOAD_FOLDER'])
