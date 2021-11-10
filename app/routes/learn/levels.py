from app.routes import bp
from app.misc.cdict import cdict
from app.models.learn.level import Level

@bp.route('/levels', methods=['GET'])
def get_levels():
    return cdict(Level.query)