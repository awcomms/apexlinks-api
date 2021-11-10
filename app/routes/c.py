import re
from app.routes import bp
from flask import request
from app.models.c import C
from app.misc.cdict import cdict
from app.misc.try_int import try_int

@bp.route('/c', methods=['GET'])
def get_c():
    query = C.query
    taken = request.args.get('taken')
    if taken:
        taken = try_int(taken)
        query = query.filter_by(taken=bool(taken))
    return cdict(query)

@bp.route('/c', methods=['PUT'])
def post_c():
    taken = request.json.get('taken')
    id = request.json.get('id')
    c = C.query.get(id)
    if not c:
        return {'error': f'country with id {id} not found'}
    c.edit({'taken': taken})
    return c.dict()