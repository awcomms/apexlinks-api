from app.routes import bp
from flask import request
from app.misc import cdict
from app.newsletter_model import Newsletter


@bp.route('/newsletter', methods=['GET'])
def newsletters():
    if request.args.get('id'):
        id = request.args.get('id')
        return Newsletter.query.get(id).dict()
    page = request.args.get('page')
    return cdict(Newsletter.query, page)
