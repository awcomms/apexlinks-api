from app.routes import bp
from flask import request
from app.auth import auth
from app.misc.cdict import cdict
from app.models.image import Image
from app.models.user import User

@bp.route('/images', methods=['POST'])
@auth
def post_image():
    urls = request.json.get('urls')
    for url in urls:
        Image(url)
    return '', 202

@bp.route('/images', methods=['GET'])
def get_images():
    page = request.args.get('page')
    return cdict(Image.query, page)