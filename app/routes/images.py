from app.routes import bp
from flask import request
from app.misc import cdict
from app.models.image import Image
from app.models.user import User

@bp.route('/images', methods=['POST'])
def post_image():
    token = request.headers.get('Authorization')
    user = User.query.filter_by(token=token).first()
    if not user or user.role != 'admin':
        return '', 401
    urls = request.json.get('urls')
    for url in urls:
        Image(url)
    return '', 202

@bp.route('/images', methods=['GET'])
def get_images():
    page = request.args.get('page')
    return cdict(Image.query, page)